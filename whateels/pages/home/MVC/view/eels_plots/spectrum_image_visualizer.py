"""
Spectrum image (datacube) visualization composer.
"""


import panel as pn
import holoviews as hv
import numpy as np
import numpy as np
import time

from numba import jit
from scipy.optimize import curve_fit
from holoviews import streams

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SpectrumImageVisualizer:
    
    # Stretch modes for layout
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'
        
    """Interactive spectrum image (datacube) visualization for DM3 files, based on Vanessa class."""
    def __init__(self, model):
        print("Initializing DM3Plots (Vanessa logic)")
        self.model = model

        self.image = None
        self.clean_dataset = None
        self.e_axis = self.model.dataset.coords[self.model.constants.ELOSS].values
        self.last_selected = {'x': 0, 'y': 0}
        self.hover_candidate = {'x': None, 'y': None, 'timestamp': 0}
        self.current_ranges = {'x_range': None, 'y_range': None}
        self._setup_widgets()
        self._setup_streams()
        self._setup_plots()
        self._setup_callbacks()

    def _setup_widgets(self):
        self.range_slider = pn.widgets.RangeSlider(
            name='Range',
            start=float(self.e_axis[0]),
            end=float(self.e_axis[-1]),
            value=(
                float(self.e_axis[0]), 
                float(self.e_axis[-1])
            )
        )
        self.range_slider.param.watch(self._update_range, 'value')

    def _setup_streams(self):
        self.range_stream = streams.RangeXY(source=None)

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

    def _setup_callbacks(self):
        streams.Tap(source=self.image).add_subscriber(self._on_tap)
        streams.PointerXY(source=self.image).add_subscriber(self._on_hover)
        pn.state.add_periodic_callback(self._debounce_callback, period=100)

    @staticmethod
    @jit
    def powerlaw(x, A, k):
        return A * x ** k

    def create_layout(self):
        return pn.Row(
            pn.Column(self.range_slider),
            self.image,
            self.spectrum_pane
        )

    def _create_image(self, clean_dataset):
        return hv.Image((np.arange(clean_dataset.shape[1]), np.arange(clean_dataset.shape[0]), clean_dataset)).opts(
            cmap='gray', colorbar=False,
            xlim=(0, clean_dataset.shape[1]-1), ylim=(0, clean_dataset.shape[0]-1),
            tools=['hover', 'tap'], invert_yaxis=True
        )

    def _capture_reset_hook(self, plot, element):
        def on_reset(event):
            self.current_ranges['x_range'] = None
            self.current_ranges['y_range'] = None
            print("Reset pressed: restoring full range.")
        plot.state.on_event('reset', on_reset)

    def _create_spectrum(self, x, y, range_values):

        selected_slice = self.model.dataset.ElectronCount[y, x, :].values
        area = hv.Area((self.e_axis, selected_slice),
                    'Energy Loss', 'Intensity (A.U.)',
                    label='Experimental Data').opts(
            fill_alpha=0.7, fill_color='royalblue', line_color='royalblue',
            line_width=2, line_alpha=0.3, tools=[]
        )
        vline1 = hv.VLine(range_values[0]).opts(color='crimson', line_dash='dashed')
        vline2 = hv.VLine(range_values[1]).opts(color='crimson', line_dash='dashed')
        overlays = area * vline1 * vline2
        if len(self.e_axis) == len(selected_slice):
            mask = (self.e_axis >= range_values[0]) & (self.e_axis <= range_values[1])
            x_fit = self.e_axis[mask]
            y_fit = selected_slice[mask]
            if len(x_fit) > 1:
                try:
                    params, _ = curve_fit(self.powerlaw, x_fit, y_fit)
                    y_fit_curve = self.powerlaw(self.e_axis, *params)
                    y_subtracted = selected_slice - y_fit_curve
                    fit_curve = hv.Curve((self.e_axis, y_fit_curve),
                                        'Energy Loss', 'Intensity (A.U.)',
                                        label='PowerLaw Fit').opts(
                        color='crimson', line_dash='solid', line_width=2, alpha=0.8
                    )
                    subtraction_area = hv.Area((self.e_axis, y_subtracted),
                                            'Energy Loss', 'Intensity (A.U.)',
                                            label='Background Subtraction').opts(
                        fill_alpha=0.9, fill_color='lightsalmon', line_color='lightsalmon',
                        line_width=2, line_alpha=0.3,
                    )
                    overlays *= fit_curve * subtraction_area
                except (RuntimeError, ValueError, TypeError) as e:
                    print(f"{e} No se pudo realizar el ajuste para el rango {range_values}.")
                    pass
        if self.range_stream.x_range is not None:
            overlays = overlays.opts(xlim=self.range_stream.x_range)
        if self.range_stream.y_range is not None:
            overlays = overlays.opts(ylim=self.range_stream.y_range)
        self.range_stream.source = overlays
        opts = dict(
            title=f"Spectrum at ({x}, {y})",
            height=350,
            responsive=True,
            show_grid=True,
            legend_position='top_right'
        )
        return overlays.opts(hooks=[self._capture_reset_hook],  **opts)

    def _update_create_spectrum(self, x, y):
        x = int(np.clip(round(x), 0, self.clean_dataset.shape[1]-1))
        y = int(np.clip(round(y), 0, self.clean_dataset.shape[0]-1))
        if (x, y) == (self.last_selected['x'], self.last_selected['y']):
            return
        self.last_selected['x'], self.last_selected['y'] = x, y
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)

    def _on_tap(self, **kwargs):
        if kwargs['x'] is not None and kwargs['y'] is not None:
            self._update_create_spectrum(kwargs['x'], kwargs['y'])

    def _on_hover(self, **kwargs):
        if kwargs['x'] is not None and kwargs['y'] is not None:
            self.hover_candidate['x'] = kwargs['x']
            self.hover_candidate['y'] = kwargs['y']
            self.hover_candidate['timestamp'] = time.time()

    def _debounce_callback(self):
        if self.hover_candidate['x'] is None:
            return
        if time.time() - self.hover_candidate['timestamp'] > 0.001:
            self._update_create_spectrum(self.hover_candidate['x'], self.hover_candidate['y'])
            self.hover_candidate['x'] = None

    def _update_range(self, event=None):
        x = self.last_selected['x']
        y = self.last_selected['y']
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)
