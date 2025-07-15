from .model import Model
from .view import View
from .services import EELSFileProcessor, EELSDataProcessor
from .handlers import InteractionHandler

import panel as pn
import holoviews as hv
from holoviews import streams
import numpy as np
from numba import jit
from holoviews.streams import Tap, PointerXY, RangeXY
import time
from scipy.optimize import curve_fit
from .visualizations import SingleSpectrumVisualizer, SpectrumLineVisualizer, SpectrumImageVisualizer

import logging
# Suppress Bokeh/Panel patch warnings by elevating log level
logging.getLogger('bokeh').setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)

class Controller:
    """
    Controller class for the home page of the WhatEELS application.
    This class orchestrates file upload events and coordinates between services.
    It delegates specific operations to specialized services while maintaining
    the overall workflow coordination.
    """
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        
        # Initialize services
        self.file_service = EELSFileProcessor(model)
        self.data_service = EELSDataProcessor()
        self.interaction_handler = InteractionHandler(model, view)
    
    def handle_file_uploaded(self, filename: str, file_content: bytes):
        """
        🔽 FileDropper Event Handler: Handle file upload from the FileDropper component.
        
        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file
        """
        # Show loading screen immediately
        self.view.show_loading()
        
        # Delegate to file service
        dataset = self.file_service.process_upload(filename, file_content)
        
        if dataset is None:
            # Reset to placeholder on error
            self.interaction_handler.reset_click_state()
            self.view.reset_plot_display()
            print(f'Error loading file: {filename}')
            return 

        # Reset interaction state for new file
        self.interaction_handler.reset_click_state()
        
        # Set dataset in model with type from dataset metadata
        dataset_type = dataset.attrs.get('dataset_type', None)
        self.model.set_dataset(dataset, dataset_type)
        
        # # Create plot based on dataset type
        # eels_plots = self.view.create_eels_plot(self.model.dataset_type)
        
        # # If plots creation failed, view already shows error so we're done
        # if eels_plots is None:
        #     print(f'Error visualizing file: {filename}')
        #     return
            
        # # Setup interaction callbacks - use tap instead of hover
        # if hasattr(self.view, 'tap_stream') and self.view.tap_stream:
        #     self.interaction_handler.setup_tap_callback(self.view.tap_stream)
        
        # # Update the view with the new plot
        # self.view.update_plot_display(eels_plots)
        # print(f'Successfully loaded and visualized: {filename}')

        # Initialize Vanessa
        self.vanessa = Vanessa(self.model)

        # Generate layout for Vanessa
        vanessa_layout = self.vanessa.create_layout()
        self.view.update_plot_display(vanessa_layout)
        # Removed invalid call to self.view.param.trigger('plot_display')

    def handle_file_removed(self, filename: str):
        """
        🔽 FileDropper Event Handler: Handle file removal from the FileDropper component.
        
        Args:
            filename: Name of the removed file
        """
        # print('File removed', filename)
        
        # Reset interaction state
        self.interaction_handler.reset_click_state()
        
        # Reset plot display to placeholder when file is removed
        self.view.reset_plot_display()
        
class Vanessa:
    def __init__(self, model):
        self.model = model
        self._STRETCH_WIDTH = 'stretch_width'
        self._STRETCH_BOTH = 'stretch_both'
        
        self.image = None
        self.clean_dataset = None        
        self.e_axis = self.model.dataset.coords[self.model.Constants.ELOSS].values
        
        self.last_selected = {'x': 0, 'y': 0}
        self.hover_candidate = {'x': None, 'y': None, 'timestamp': 0}
        self.current_ranges = {'x_range': None, 'y_range': None}

        # self._last_update_time = 0.0
        # self._debounce_interval = 0.1  # seconds
        
        pn.extension()
        
        # Inicializar componentes
        self._setup_widgets()
        self._setup_streams()
        self._setup_plots()
        self._setup_callbacks()
        # Construir layout y almacenarlo
        self.layout = self.create_layout()
        
    def _setup_widgets(self):
        """Configura los widgets de la interfaz."""
        self.range_slider = pn.widgets.RangeSlider(
            name='Range', 
            start=float(self.e_axis[0]), 
            end=float(self.e_axis[-1]),
            value=(float(self.e_axis[0]), float(self.e_axis[-1]))
        )
        
        # Configurar callback del slider
        self.range_slider.param.watch(self._update_range, 'value')
    
    def _setup_streams(self):
        """Configura los streams de HoloViews."""
        self.range_stream = RangeXY(source=None)

    def _setup_plots(self):
        image_data = self.model.dataset.ElectronCount.sum(self.model.Constants.ELOSS)
        
        # Clean image data
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        
        # Clean coordinates
        x_coords = self.model.dataset.coords[self.model.Constants.AXIS_X]
        y_coords = self.model.dataset.coords[self.model.Constants.AXIS_Y]
        
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        y_coords = y_coords.where(np.isfinite(y_coords), 0.0)
        
        # Create clean dataset
        self.clean_dataset = image_data.assign_coords({
            self.model.Constants.AXIS_X: x_coords,
            self.model.Constants.AXIS_Y: y_coords
        })

        # Initialize panes
        self.image = self._create_image(self.clean_dataset)
        spec_hv = self._create_spectrum(0, 0, self.range_slider.value)
        self.spectrum_pane = pn.pane.HoloViews(spec_hv, sizing_mode=self._STRETCH_WIDTH)

    
    def _setup_callbacks(self):
        """Configura los callbacks y subscribers."""
        # Configurar streams de interacción
        Tap(source=self.image).add_subscriber(self._on_tap)
        PointerXY(source=self.image).add_subscriber(self._on_hover)
        
        # Configurar callback periódico para debounce
        pn.state.add_periodic_callback(self._debounce_callback, period=100)
    
    @staticmethod
    @jit
    def powerlaw(x, A, k):
        return A * x ** k

    def create_layout(self):
        """Create layout for Vanessa visualization"""
        # Only define layout here, callbacks handled elsewhere
        layout = pn.Row(
            pn.Column(self.range_slider),
            self.image,
            self.spectrum_pane
        )

        return layout

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

    # --- Plot Matrix B ---
    def _create_spectrum(self, x, y, range_values):
        selected_slice = self.model.dataset.ElectronCount[y, x, :].values
        
        # Curva original
        area = hv.Area((self.e_axis, selected_slice), 
                    'Energy Loss', 'Intensity (A.U.)',
                    label='Experimental Data').opts(
            fill_alpha=0.7, fill_color='royalblue', line_color='royalblue',
            line_width=2, line_alpha=0.3, tools=[]
        )
        
        # Líneas de rango
        vline1 = hv.VLine(range_values[0]).opts(color='crimson', line_dash='dashed')
        vline2 = hv.VLine(range_values[1]).opts(color='crimson', line_dash='dashed')
        
        overlays = area * vline1 * vline2

        # Ajuste de fondo tipo powerlaw en la región seleccionada
        if len((self.e_axis) == len(selected_slice)):
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
                    # No se pudo ajustar el powerlaw, se omite
                    print(f"{e} No se pudo realizar el ajuste para el rango {range_values}.")
                    pass

        # Aplicar zoom anterior si hay
        if self.range_stream.x_range is not None:
            overlays = overlays.opts(xlim=self.range_stream.x_range)
        if self.range_stream.y_range is not None:
            overlays = overlays.opts(ylim=self.range_stream.y_range)

        self.range_stream.source = overlays  # Actualiza la fuente del stream

        opts = dict(
            title=f"Spectrum at ({x}, {y})",
            height=350,
            responsive=True,
            show_grid=True,
            legend_position='top_right'
        )

        return overlays.opts(hooks=[self._capture_reset_hook],  **opts)
    
    # --- Actualizar B ---
    def _update_create_spectrum(self, x, y):
        x = int(np.clip(round(x), 0, self.clean_dataset.shape[1]-1))
        y = int(np.clip(round(y), 0, self.clean_dataset.shape[0]-1))
        if (x, y) == (self.last_selected['x'], self.last_selected['y']):
            return  # Skip redundant updates
        self.last_selected['x'], self.last_selected['y'] = x, y
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)

    # --- Callbacks ---
    def _on_tap(self, **kwargs):
        if kwargs['x'] is not None and kwargs['y'] is not None:
            self._update_create_spectrum(kwargs['x'], kwargs['y'])

    def _on_hover(self, **kwargs):
        if kwargs['x'] is not None and kwargs['y'] is not None:
            self.hover_candidate['x'] = kwargs['x']
            self.hover_candidate['y'] = kwargs['y']
            self.hover_candidate['timestamp'] = time.time()

    def _debounce_callback(self):
        """Callback con debounce para el hover."""
        if self.hover_candidate['x'] is None: 
            return
        if time.time() - self.hover_candidate['timestamp'] > 0.001:
            self._update_create_spectrum(self.hover_candidate['x'], self.hover_candidate['y'])
            self.hover_candidate['x'] = None

    # --- Rango del slider ---
    def _update_range(self, event=None):
        x = self.last_selected['x']
        y = self.last_selected['y']
        self.spectrum_pane.object = self._create_spectrum(x, y, self.range_slider.value)
    
    def get_current_spectrum(self):
        """Retorna el espectro actualmente seleccionado."""
        x, y = self.last_selected['x'], self.last_selected['y']
        return self.B[y, x, :]

    def get_current_position(self):
        """Retorna la posición actualmente seleccionada."""
        return self.last_selected['x'], self.last_selected['y']