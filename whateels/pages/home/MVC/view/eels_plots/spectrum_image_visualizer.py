"""
Spectrum image (datacube) visualization composer.
"""

import panel as pn
import param
import holoviews as hv
import numpy as np
import time

from numba import jit
from scipy.optimize import curve_fit
from holoviews import streams
from .abstract_eels_visualizer import AbstractEELSVisualizer
from typing import override

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SpectrumImageVisualizer(AbstractEELSVisualizer):
    """
    Interactive spectrum image (datacube) visualization for DM3 files.
    
    Features:
      - Interactive spectrum selection via hover (debounced with _HOVER_DEBOUNCE_DELAY).
      - Efficient spectrum updates using HoloViews DynamicMap and custom stream.
      - Powerlaw background fitting and subtraction in selected range.
      - Responsive Panel layout with stretch sizing.
      - Customizable range slider and dataset info panel.
      - Designed for EELS data, based on the Vanessa class architecture.
    """
    
    # Axis and range keys
    _X_AXIS = "x"
    _Y_AXIS = "y"
    _TIMESTAMP = "timestamp"
    _X_RANGE = "x_range"
    _Y_RANGE = "y_range"

    # Panel sizing modes
    _STRETCH_WIDTH = "stretch_width"
    _STRETCH_BOTH = "stretch_both"
    _STRETCH_HEIGHT = "stretch_height"

    # Widget names
    _WIDGET_RANGE = "Range"
    _WIDGET_BEAM_ENERGY = "BeamEnergy-E0 keV"
    _WIDGET_CONV_ANGLE = "Convergence-α mrad"

    # Widget options
    _WIDGET_OPTIONS = [0, 1, 2, 3, 4, 5]
    _WIDGET_DEFAULT = 0

    # Plot labels
    _LABEL_EXPERIMENTAL = "Experimental Data"
    _LABEL_POWERLAW = "PowerLaw Fit"
    _LABEL_SUBTRACTION = "Background Subtraction"
    _LABEL_INCONSISTENT = "Inconsistent Data Length"
    _LABEL_SPECTRUM = "Spectrum at"
    _XLABEL = "Energy Loss"
    _YLABEL = "Intensity (A.U.)"

    # HoloViews style
    _VLINE_DASH = "dashed"
    _POWERLAW_DASH = "solid"
    _AREA_ALPHA = 0.7
    _AREA_LINE_ALPHA = 0.3
    _POWERLAW_ALPHA = 0.8
    _SUBTRACTION_ALPHA = 0.9
    _SUBTRACTION_LINE_ALPHA = 0.3
    _SUBTRACTION_LINE_WIDTH = 2
    _AREA_LINE_WIDTH = 2
    _POWERLAW_LINE_WIDTH = 2
    _SPECTRUM_HEIGHT = 350
    _LEGEND_POSITION = "top_right"
    _HOVER_DEBOUNCE_DELAY = 0.15  # Debounce delay (seconds) for hover spectrum updates

    # Miscellaneous
    _IMAGE_CMAP = "gray"
    _IMAGE_COLORBAR = False
    _IMAGE_TOOLS = ["hover"]
    _IMAGE_HEIGHT = 400
    _IMAGE_INVERT_Y = True
    _IMAGE_RESPONSIVE = False
    _IMAGE_ASPECT = "equal"
    _GENERIC_CONTAINER_CLASS = ["generic-container"]
    _DATASET_INFO_HEADER_CLASS = ["dataset-info-header"]
    _DATASET_INFO_CLASS = ["dataset-info", "animated"]
    _DATASET_INFO_TITLE = "<h5 class=\"dataset-info-title\">Dataset Information</h5>"
    _DATASET_DETAILS_NAME = "Dataset Details"
    _DATASET_DETAILS_WIDTH = 350
    _DATASET_DETAILS_HEIGHT = 250
    _DATASET_DETAILS_POSITION = "center"
    _DATASET_DETAILS_HEADER = "### More Dataset Details"
    _DATASET_DETAILS_PLACEHOLDER = "(Add more details here as needed)"

    def __init__(self, model):
        self.model = model
        self.image = None
        self.clean_dataset = None
        self.e_axis = self.model.dataset.coords[self.model.constants.ELOSS].values
        self.last_selected = {self._X_AXIS: 0, self._Y_AXIS: 0}
        self.hover_candidate = {self._X_AXIS: None, self._Y_AXIS: None, self._TIMESTAMP: 0}
        self.current_ranges = {self._X_RANGE: None, self._Y_RANGE: None}

        # Setup widgets, plots, and callbacks
        self._setup_widgets()
        self._setup_plots()
        self._setup_callbacks()

    # --- Widget Setup ---
    def _setup_widgets(self):
        self.range_slider = pn.widgets.RangeSlider(
            name=self._WIDGET_RANGE,
            start=float(self.e_axis[0]),
            end=float(self.e_axis[-1]),
            value=(float(self.e_axis[0]), float(self.e_axis[-1])),
            sizing_mode=self._STRETCH_WIDTH,
        )
        self.range_slider.param.watch(self._update_range, 'value')
        # Widgets adicionales movidos al panel de info de datos
        self.beam_energy = pn.widgets.Select(
            name=self._WIDGET_BEAM_ENERGY,
            options=self._WIDGET_OPTIONS,
            value=self._WIDGET_DEFAULT,
            sizing_mode=self._STRETCH_WIDTH
        )
        self.convergence_angle = pn.widgets.Select(
            name=self._WIDGET_CONV_ANGLE,
            options=self._WIDGET_OPTIONS,
            value=self._WIDGET_DEFAULT,
            sizing_mode=self._STRETCH_WIDTH
        )

    # --- Plot Setup ---
    def _setup_plots(self):
        image_data = self.model.dataset.ElectronCount.sum(self.model.constants.ELOSS)
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        x_coords = self.model.dataset.coords[self.model.constants.AXIS_X]
        y_coords = self.model.dataset.coords[self.model.constants.AXIS_Y]
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        y_coords = y_coords.where(np.isfinite(y_coords), 0.0)
        self.clean_dataset = image_data.assign_coords({
            self.model.constants.AXIS_X: x_coords,
            self.model.constants.AXIS_Y: y_coords
        })
        self.image = self._create_image(self.clean_dataset)
        # Use DynamicMap for efficient spectrum updates
        self.spectrum_stream = streams.Stream.define(
            self._LABEL_SPECTRUM.replace(" ", ""),
            x=0,
            y=0,
            range_values=(float(self.e_axis[0]), float(self.e_axis[-1]))
        )()
        self.spectrum_dynamicmap = hv.DynamicMap(
            lambda x, y, range_values: self._create_spectrum(x, y, range_values),
            streams=[self.spectrum_stream]
        )
        self.spectrum_pane = pn.pane.HoloViews(self.spectrum_dynamicmap, sizing_mode=self._STRETCH_BOTH)

    # --- Callback Setup ---
    def _setup_callbacks(self):
        streams.PointerXY(source=self.image).add_subscriber(self._on_hover)

    # --- Math Utility ---
    @staticmethod
    @jit
    def powerlaw(x, A, k):
        return A * x ** k

    @override
    def create_plots(self):
        """Create the main layout for the spectrum image visualizer."""
        return pn.Column(
            pn.Row(
                pn.Column(
                    self.image,
                    css_classes=self._GENERIC_CONTAINER_CLASS,
                    sizing_mode=self._STRETCH_HEIGHT,
                    margin=(0, 10, 0, 0)
                ),
                pn.Column(
                    pn.Row(
                        self.spectrum_pane,
                        sizing_mode=self._STRETCH_BOTH,
                    ),
                    pn.Row(
                        self.range_slider,
                        sizing_mode=self._STRETCH_WIDTH,
                        margin=(0, 26, 0, 70)
                    ),
                    sizing_mode=self._STRETCH_BOTH,
                    css_classes=self._GENERIC_CONTAINER_CLASS
                ),
                sizing_mode=self._STRETCH_BOTH,
                margin=(10, 0, 0, 0)
            )
        )
    
    @override
    def create_dataset_info(self):
        attrs = self.model.dataset.attrs if self.model.dataset is not None else {}
        shape = attrs.get('shape', 'N/A')
        beam_energy = attrs.get('beam_energy', 'N/A')
        convergence_angle = attrs.get('convergence_angle', 'N/A')
        collection_angle = attrs.get('collection_angle', 'N/A')

        # Main info panel
        header = pn.Row(
            pn.pane.HTML(self._DATASET_INFO_TITLE, sizing_mode=self._STRETCH_WIDTH),
            sizing_mode=self._STRETCH_WIDTH,
            css_classes=self._DATASET_INFO_HEADER_CLASS
        )

        dataset_info = pn.Column(
            header,
            pn.Spacer(height=5),
            pn.Row(
                pn.pane.Str("Shape:"),
                pn.pane.Str(shape),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.pane.Str("Beam Energy:"),
                pn.pane.Str(f"{beam_energy} keV"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.pane.Str("Convergence Angle:"),
                pn.pane.Str(f"{convergence_angle} mrad"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.pane.Str("Collection Angle:"),
                pn.pane.Str(f"{collection_angle} mrad"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            sizing_mode=self._STRETCH_WIDTH,
            css_classes=self._DATASET_INFO_CLASS
        )
        return dataset_info

    # --- Image Plot ---
    def _create_image(self, clean_dataset):
        """
        Create a HoloViews image plot from the cleaned dataset.
        Args:
            clean_dataset: 2D array-like, shape (height, width)
        Returns:
            hv.Image: Interactive image plot with hover/tap tools.
        """
        height, width = clean_dataset.shape
        x_axis = np.arange(width)
        y_axis = np.arange(height)
        image = hv.Image((x_axis, y_axis, clean_dataset)).opts(
            cmap=self._IMAGE_CMAP,
            colorbar=self._IMAGE_COLORBAR,
            xlim=(0, width - 1),
            ylim=(0, height - 1),
            tools=self._IMAGE_TOOLS,
            height=self._IMAGE_HEIGHT,
            invert_yaxis=self._IMAGE_INVERT_Y,
            responsive=self._IMAGE_RESPONSIVE,
            aspect=self._IMAGE_ASPECT  # Ensure square pixels
        )
        return image

    # --- Reset Button Callback ---
    def _capture_reset_hook(self, plot, element):
        def on_reset(event):
            self.current_ranges['x_range'] = None
            self.current_ranges['y_range'] = None
            print("Reset pressed: restoring full range.")
        plot.state.on_event('reset', on_reset)

    # --- Spectrum Plot ---
    def _create_spectrum(self, x, y, range_values):
        """
        Create the spectrum plot for a given (x, y) position and range.
        Includes experimental data, range markers, and optional powerlaw fit/subtraction.
        """
        # Extract the spectrum at the selected pixel
        selected_spectrum = self.model.dataset.ElectronCount[y, x, :].values

        # Main experimental area plot
        area = hv.Area(
            (self.e_axis, selected_spectrum),
            self._XLABEL, self._YLABEL,
            label=self._LABEL_EXPERIMENTAL
        ).opts(
            fill_alpha=self._AREA_ALPHA,
            fill_color=self.model.colors.ROYALBLUE,
            line_color=self.model.colors.ROYALBLUE,
            line_width=self._AREA_LINE_WIDTH,
            line_alpha=self._AREA_LINE_ALPHA,
            tools=[]
        )

        # Range markers
        vline1 = hv.VLine(range_values[0]).opts(color=self.model.colors.CRIMSON, line_dash=self._VLINE_DASH)
        vline2 = hv.VLine(range_values[1]).opts(color=self.model.colors.CRIMSON, line_dash=self._VLINE_DASH)
        overlays = area * vline1 * vline2
        
        if len(self.e_axis) != len(selected_spectrum):
            return self._inconsistent_overlay_opts(overlays, x, y)

        # Powerlaw fit and subtraction (if possible)
        # Mask for selected range
        mask = (self.e_axis >= range_values[0]) & (self.e_axis <= range_values[1])
        x_fit = self.e_axis[mask]
        y_fit = selected_spectrum[mask]

        if len(x_fit) <= 0:
            return self._inconsistent_overlay_opts(overlays, x, y)

        try:
            # Fit powerlaw to selected range
            params, _ = curve_fit(self.powerlaw, x_fit, y_fit)
            y_fit_curve = self.powerlaw(self.e_axis, *params)
            y_subtracted = selected_spectrum - y_fit_curve

            # Powerlaw fit curve
            fit_curve = hv.Curve(
                (self.e_axis, y_fit_curve),
                self._XLABEL, self._YLABEL,
                label=self._LABEL_POWERLAW
            ).opts(
                color=self.model.colors.CRIMSON,
                line_dash=self._POWERLAW_DASH,
                line_width=self._POWERLAW_LINE_WIDTH,
                alpha=self._POWERLAW_ALPHA
            )

            # Background subtraction area
            subtraction_area = hv.Area(
                (self.e_axis, y_subtracted),
                self._XLABEL, self._YLABEL,
                label=self._LABEL_SUBTRACTION
            ).opts(
                fill_alpha=self._SUBTRACTION_ALPHA,
                fill_color=self.model.colors.LIGHTSALMON,
                line_color=self.model.colors.LIGHTSALMON,
                line_width=self._SUBTRACTION_LINE_WIDTH,
                line_alpha=self._SUBTRACTION_LINE_ALPHA
            )

            overlays *= fit_curve * subtraction_area
        except (RuntimeError, ValueError, TypeError) as e:
            print(f"{e} No se pudo realizar el ajuste para el rango {range_values}.")
            return self._inconsistent_overlay_opts(overlays, x, y)

        # Plot options
        opts = dict(
            title=f"{self._LABEL_SPECTRUM} ({x}, {y})",
            responsive=True,
            show_grid=True,
            legend_position=self._LEGEND_POSITION
        )
        return overlays.opts(hooks=[self._capture_reset_hook], **opts)

    # --- Interactive Spectrum Update ---
    def _update_create_spectrum(self, x, y):
        # Clamp and round coordinates to valid integer indices
        max_x = self.clean_dataset.shape[1] - 1
        max_y = self.clean_dataset.shape[0] - 1
        x_idx = int(np.clip(round(x), 0, max_x))
        y_idx = int(np.clip(round(y), 0, max_y))

        # Only update if the selection has changed
        if (x_idx, y_idx) == (self.last_selected[self._X_AXIS], self.last_selected[self._Y_AXIS]):
            return

        # Store last selected coordinates
        self.last_selected[self._X_AXIS] = x_idx
        self.last_selected[self._Y_AXIS] = y_idx

        # Update the DynamicMap stream with new values
        self.spectrum_stream.event(x=x_idx, y=y_idx, range_values=self.range_slider.value)

    # --- Hover Callback ---
    def _on_hover(self, **kwargs):

        coord_x = kwargs.get(self._X_AXIS)
        coord_y = kwargs.get(self._Y_AXIS)

        if coord_x is None or coord_y is None:
            return

        now = time.time()
        last_time = self.hover_candidate.get(self._TIMESTAMP, 0)
        # Only update if at least _HOVER_DEBOUNCE_DELAY seconds have passed since last update
        if now - last_time >= self._HOVER_DEBOUNCE_DELAY:
            self.hover_candidate[self._X_AXIS] = coord_x
            self.hover_candidate[self._Y_AXIS] = coord_y
            self.hover_candidate[self._TIMESTAMP] = now
            self._update_create_spectrum(coord_x, coord_y)

    def _inconsistent_overlay_opts(self, overlays, x, y):
        """
        Return overlays with options for inconsistent data length or fit failure.
        """
        return overlays.opts(
            title=f"{self._LABEL_SPECTRUM} ({x}, {y}) - {self._LABEL_INCONSISTENT}",
            responsive=True,
            show_grid=True,
            legend_position=self._LEGEND_POSITION
        )

    # --- Range Slider Callback ---
    def _update_range(self, event=None):
        x = self.last_selected[self._X_AXIS]
        y = self.last_selected[self._Y_AXIS]
        # Update the DynamicMap stream with new range values
        self.spectrum_stream.event(x=x, y=y, range_values=self.range_slider.value)
