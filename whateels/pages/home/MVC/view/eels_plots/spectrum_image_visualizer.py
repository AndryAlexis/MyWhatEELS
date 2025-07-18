"""
Spectrum image (datacube) visualization composer.
"""

import panel as pn
import holoviews as hv
import numpy as np
import time
from numba import jit
from scipy.optimize import curve_fit
from holoviews import streams

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)


class SpectrumImageVisualizer:
    """
    Interactive spectrum image (datacube) visualization for DM3 files, based on Vanessa class.
    """
    
    _X_AXIS = 'x'
    _Y_AXIS = 'y'
    _TIMESTAMP = 'timestamp'
    _X_RANGE = 'x_range'
    _Y_RANGE = 'y_range'
    
    # Stretch modes for layout
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'

    # Plot labels and style constants
    _LABEL_EXPERIMENTAL = 'Experimental Data'
    _LABEL_POWERLAW = 'PowerLaw Fit'
    _LABEL_SUBTRACTION = 'Background Subtraction'
    _XLABEL = 'Energy Loss'
    _YLABEL = 'Intensity (A.U.)'
    # Color constants removed; use self.model.colors for all color references
    _VLINE_DASH = 'dashed'
    _POWERLAW_DASH = 'solid'
    _AREA_ALPHA = 0.7
    _AREA_LINE_ALPHA = 0.3
    _POWERLAW_ALPHA = 0.8
    _SUBTRACTION_ALPHA = 0.9
    _SUBTRACTION_LINE_ALPHA = 0.3
    _SUBTRACTION_LINE_WIDTH = 2
    _AREA_LINE_WIDTH = 2
    _POWERLAW_LINE_WIDTH = 2
    _SPECTRUM_HEIGHT = 350
    _LEGEND_POSITION = 'top_right'

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
            name='Range',
            start=float(self.e_axis[0]),
            end=float(self.e_axis[-1]),
            value=(float(self.e_axis[0]), float(self.e_axis[-1]))
        )
        self.range_slider.param.watch(self._update_range, 'value')

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
        spec_hv = self._create_spectrum(0, 0, self.range_slider.value)
        self.spectrum_pane = pn.pane.HoloViews(spec_hv, sizing_mode=self._STRETCH_WIDTH)

    # --- Callback Setup ---
    def _setup_callbacks(self):
        streams.Tap(source=self.image).add_subscriber(self._on_tap)
        streams.PointerXY(source=self.image).add_subscriber(self._on_hover)
        pn.state.add_periodic_callback(self._debounce_callback, period=100)

    # --- Math Utility ---
    @staticmethod
    @jit
    def powerlaw(x, A, k):
        return A * x ** k

    # --- Layout ---
    def create_layout(self):
        return pn.Row(
            pn.Column(self.range_slider),
            self.image,
            self.spectrum_pane
        )

    # --- Image Plot ---
    def _create_image(self, clean_dataset):
        return hv.Image((np.arange(clean_dataset.shape[1]), np.arange(clean_dataset.shape[0]), clean_dataset)).opts(
            cmap='gray', colorbar=False,
            xlim=(0, clean_dataset.shape[1]-1), ylim=(0, clean_dataset.shape[0]-1),
            tools=['hover', 'tap'], invert_yaxis=True
        )

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

        # Powerlaw fit and subtraction (if possible)
        if len(self.e_axis) == len(selected_spectrum):
            # Mask for selected range
            mask = (self.e_axis >= range_values[0]) & (self.e_axis <= range_values[1])
            x_fit = self.e_axis[mask]
            y_fit = selected_spectrum[mask]

            if len(x_fit) > 1:
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
                    # If fit fails, just show the experimental data and range markers
                    pass

        # Plot options
        opts = dict(
            title=f"Spectrum at ({x}, {y})",
            height=self._SPECTRUM_HEIGHT,
            responsive=True,
            show_grid=True,
            legend_position=self._LEGEND_POSITION
        )
        return overlays.opts(hooks=[self._capture_reset_hook], **opts)

    # --- Interactive Spectrum Update ---
    def _update_create_spectrum(self, x, y):
        x = int(np.clip(round(x), 0, self.clean_dataset.shape[1]-1))
        y = int(np.clip(round(y), 0, self.clean_dataset.shape[0]-1))
        if (x, y) == (self.last_selected[self._X_AXIS], self.last_selected[self._Y_AXIS]):
            return
        self.last_selected[self._X_AXIS], self.last_selected[self._Y_AXIS] = x, y
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)

    # --- Tap Callback ---
    def _on_tap(self, **kwargs):
        if kwargs[self._X_AXIS] is not None and kwargs[self._Y_AXIS] is not None:
            self._update_create_spectrum(kwargs[self._X_AXIS], kwargs[self._Y_AXIS])

    # --- Hover Callback ---
    def _on_hover(self, **kwargs):
        if kwargs[self._X_AXIS] is not None and kwargs[self._Y_AXIS] is not None:
            self.hover_candidate[self._X_AXIS] = kwargs[self._X_AXIS]
            self.hover_candidate[self._Y_AXIS] = kwargs[self._Y_AXIS]
            self.hover_candidate[self._TIMESTAMP] = time.time()

    # --- Debounce Callback ---
    def _debounce_callback(self):
        if self.hover_candidate[self._X_AXIS] is None:
            return
        if time.time() - self.hover_candidate[self._TIMESTAMP] > 0.001:
            self._update_create_spectrum(self.hover_candidate[self._X_AXIS], self.hover_candidate[self._Y_AXIS])
            self.hover_candidate[self._X_AXIS] = None

    # --- Range Slider Callback ---
    def _update_range(self, event=None):
        x = self.last_selected[self._X_AXIS]
        y = self.last_selected[self._Y_AXIS]
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)
