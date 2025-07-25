from ..model import Model
from .eels_plot_factory import EELSPlotFactory
import panel as pn
import holoviews as hv
from whateels.components import FileDropper

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class View:
    """
    View class for the home page of the WhatEELS application.
    
    This class is responsible for:
    - UI rendering and layout presentation
    - Managing UI state transitions (placeholders, loading screens, plots)
    - Coordinating with plot factories for EELS displays
    
    The View receives data from the Model and rendering commands from the Controller,
    but does not make decisions about what to display - it only renders what it's told to.
    """
    
    # Constants for sizing modes
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'

    def __init__(self, model: Model):
        # Callbacks dictionary to hold event handlers
        self.callbacks = {}
        # Placeholder for dataset attributes info in sidebar (widgets will be placed here)
        self._dataset_info_pane = pn.Column(sizing_mode=self._STRETCH_WIDTH)
        self.model = model

        # Factory for creating EELS plots
        self.eels_plot_factory = EELSPlotFactory(model, self)
        
        # Main layout that will switch between UI states
        self._main_container_layout = None
        
        # Placeholders for _main_container_layout states
        self._loading_placeholder = None
        self._no_file_placeholder = None
        self._error_placeholder = None

        # Active plotter (to access interaction streams)
        self.active_plotter = None
        
        # Initialize UI components
        self._init_visualization_components()

    @property
    def sidebar(self) -> pn.Column:
        return self._sidebar_layout()
    
    @property
    def main(self) -> pn.Column:
        return self._main_layout()
    
    @property
    def callbacks(self) -> dict:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("Callbacks must be a dictionary")
        self._callbacks = value
        
    @property
    def tap_stream(self):
        """Get tap stream from active plotter"""
        if self.active_plotter and hasattr(self.active_plotter, 'tap_stream'):
            return self.active_plotter.tap_stream
        return None
    
    @property
    def spectrum_pane(self):
        """Get spectrum pane from active plotter"""
        if self.active_plotter and hasattr(self.active_plotter, 'spectrum_pane'):
            return self.active_plotter.spectrum_pane
        return None
    
    def _init_visualization_components(self):
        """
        Initialize main visualization container and placeholders.
        
        Creates:
        - no_file_placeholder: shown when no file loaded
        - loading_placeholder: shown during file processing  
        - main_layout: container that switches between states
        """
        # Placeholder for when no file is loaded
        self._no_file_placeholder = pn.pane.HTML(
            self.model.placeholders.NO_FILE_LOADED,
            sizing_mode=self._STRETCH_BOTH
        )
        
        # Loading placeholder for when file is being processed
        self._loading_placeholder = pn.Column(
            pn.pane.HTML(
                self.model.placeholders.LOADING_FILE,
                sizing_mode=self._STRETCH_BOTH
            ),
            sizing_mode=self._STRETCH_BOTH,
        )
        
        # Error placeholder for when an error occurs
        self._error_placeholder = pn.pane.HTML(
            self.model.placeholders.ERROR_FILE,
            sizing_mode=self._STRETCH_BOTH
        )
    
    def _sidebar_layout(self):
        """Create and return the sidebar layout"""
        file_dropper = FileDropper(
            valid_extensions=self.model.file_dropper.VALID_EXTENSIONS,
            reject_message=self.model.file_dropper.REJECT_MESSAGE,
            success_message=self.model.file_dropper.SUCCESS_MESSAGE,
            feedback_message=self.model.file_dropper.FEEDBACK_MESSAGE,
            on_file_uploaded_callback=self.callbacks.get(self.model.callbacks.FILE_UPLOADED),
            on_file_removed_callback=self.callbacks.get(self.model.callbacks.FILE_REMOVED)
        )
        
        return pn.Column(
            file_dropper,
            self._dataset_info_pane,  # Información de datos debajo del file_dropper
            sizing_mode=self._STRETCH_WIDTH
        )
    
    def _main_layout(self):
        """Create and return the main content area"""
    
        self._main_container_layout = pn.Column(
            self._no_file_placeholder,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout

    def update_plot_display(self, plot_component):
        """Update the main area with a new plot component"""
        self._main_container_layout.clear()
        self._main_container_layout.append(plot_component)
    
    def show_loading(self):
        """Show loading screen while processing file"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._loading_placeholder)
    
    def reset_plot_display(self):
        """Reset the main area to show the placeholder"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._no_file_placeholder)
        
    def show_error(self):
        """Show error placeholder when an error occurs"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._error_placeholder)
    
    def create_eels_plot(self, dataset_type: str):
        """
        Create EELS plots based on dataset type.
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate plot visualization, or None
            if an error occurred (in which case the view will already show an error)
        """
        plot_result = self.eels_plot_factory.create_plots(dataset_type)
        
        if plot_result is None:
            # Factory encountered an error, view already updated to show error
            # Just return None to signal that no new component is needed
            return None
            
        # Store reference to active plotter for interaction access
        # Store reference to active plotter for interaction access
        self.active_plotter = self.eels_plot_factory.current_plot_renderer
        # Populate dataset info pane with widget controls if available
        # Actualizar panel de información con valores de E0, alpha y beta
        try:
            self._dataset_info_pane.clear()
            attrs = self.model.dataset.attrs if self.model.dataset else {}
            image_name = attrs.get('image_name', '')
            shape = attrs.get('shape', [])
            shape = [shape[1], shape[0], shape[2]]
            e0 = attrs.get('beam_energy', 0)
            alpha = attrs.get('convergence_angle', 0)
            beta = attrs.get('collection_angle', 0)
            # HTML table with inputs for dataset attributes
            html_rows = [
                '<tr>'
                '<td style="border:none;padding:2px;width:120px;"><b>Image Info</b></td>'
                '<td style="border:none;padding:2px;">'
                '<button style="font-size:11px;width:100%;">more ...</button>'
                '</td>'
                '</tr>',
                f'<tr>'
                '<td style="border:none;padding:2px;"><b>Name:</b></td>'
                f'<td style="border:none;padding:2px;">{image_name}</td>'
                '</tr>',
                f'<tr>'
                '<td style="border:none;padding:2px;"><b>Shape:</b></td>'
                f'<td style="border:none;padding:2px;">{shape}</td>'
                '</tr>',
                f'<tr>'
                '<td style="border:none;padding:2px;"><b>Beam Energy:</b></td>'
                f'<td style="border:none;padding:2px;text-align:right;">'
                f'<input type="text" inputmode="decimal" value="{e0}" style="font-size:12px;width:100%;">'
                '</td>'
                '</tr>',
                f'<tr>'
                '<td style="border:none;padding:2px;"><b>Convergence Angle:</b></td>'
                f'<td style="border:none;padding:2px;text-align:right;">'
                f'<input type="text" inputmode="decimal" value="{alpha}" style="font-size:12px;width:100%;">'
                '</td>'
                '</tr>',
                f'<tr>'
                '<td style="border:none;padding:2px;"><b>Collection Angle:</b></td>'
                f'<td style="border:none;padding:2px;text-align:right;">'
                f'<input type="text" inputmode="decimal" value="{beta}" style="font-size:12px;width:100%;">'
                '</td>'
                '</tr>',
            ]
            html_table = (
                '<table style="border-collapse:collapse;font-size:12px;">'
                + ''.join(html_rows) +
                '</table>'
            )
            self._dataset_info_pane.append(pn.pane.HTML(html_table, sizing_mode=self._STRETCH_WIDTH))
        except Exception:
            # No interrumpir si falla la obtención de atributos
            pass
        return plot_result
    
    def show_single_spectrum(self, visualizer):
        spectrum_data = visualizer.get_spectrum_data()
        spectrum_curve = hv.Curve(
            spectrum_data,
            kdims=[self.model.constants.ELOSS],
            vdims=[self.model.constants.ELECTRON_COUNT]
        ).opts(
            width=800,
            height=400,
            color=self.model.colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='EELS Spectrum'
        )
        spectrum_pane = pn.pane.HoloViews(spectrum_curve, sizing_mode=self._STRETCH_WIDTH)
        self.update_plot_display(
            pn.Column(
                spectrum_pane,
                sizing_mode=self._STRETCH_BOTH
            )
        )