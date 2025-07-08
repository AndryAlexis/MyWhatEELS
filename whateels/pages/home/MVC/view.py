from .model import Model
from .visualization_factory import EELSVisualizationFactory
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
    - Managing UI state transitions (placeholders, loading screens, visualizations)
    - Coordinating with visualization factories for EELS displays
    
    The View receives data from the Model and rendering commands from the Controller,
    but does not make decisions about what to display - it only renders what it's told to.
    """
    
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'

    def __init__(self, model: Model):
        self.model = model
        self.callbacks = {}
        self.visualization_factory = EELSVisualizationFactory(model)
        
        # Current visualizer (to access interaction streams)
        self.current_visualizer = None
        
        # Initialize UI components
        self._init_visualization_components()
    
    def _init_visualization_components(self):
        """
        Initialize main visualization container and placeholders.
        
        Creates:
        - no_file_placeholder: shown when no file loaded
        - loading_placeholder: shown during file processing  
        - main_layout: container that switches between states
        """
        # Placeholder for when no file is loaded
        self.no_file_placeholder = pn.pane.HTML(
            self.model.Placeholders.NO_FILE_LOADED,
            sizing_mode=self._STRETCH_BOTH
        )
        
        # Loading placeholder for when file is being processed
        self.loading_placeholder = pn.Column(
            pn.pane.HTML(
                self.model.Placeholders.LOADING_FILE,
                sizing_mode=self._STRETCH_BOTH
            ),
            sizing_mode=self._STRETCH_BOTH,
        )
        
        # Container that will hold placeholder, loading, or actual visualization
        self.main_layout = pn.Column(
            self.no_file_placeholder,
            sizing_mode=self._STRETCH_BOTH
        )
    
    def _sidebar_layout(self):
        """Create and return the sidebar layout"""
        file_dropper = FileDropper(
            valid_extensions=Model.FileDropper.VALID_EXTENSIONS,
            reject_message=Model.FileDropper.REJECT_MESSAGE,
            success_message=Model.FileDropper.SUCCESS_MESSAGE,
            feedback_message=Model.FileDropper.FEEDBACK_MESSAGE,
            on_file_uploaded_callback=self.callbacks.get(Model.Callbacks.FILE_UPLOADED),
            on_file_removed_callback=self.callbacks.get(Model.Callbacks.FILE_REMOVED)
        )
        
        return pn.Column(file_dropper, sizing_mode=self._STRETCH_WIDTH)
    
    def _main_layout(self):
        """Create and return the main content area"""
        return self.main_layout
    
    @property
    def sidebar(self) -> pn.Column:
        return self._sidebar_layout()
    
    @property
    def main(self):
        return self._main_layout()
    
    @property
    def callbacks(self) -> dict:
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("Callbacks must be a dictionary")
        self._callbacks = value
    
    def update_visualization(self, visualization_component):
        """Update the main area with a new visualization component"""
        self.main_layout.clear()
        self.main_layout.append(visualization_component)
    
    def show_loading(self):
        """Show loading screen while processing file"""
        self.main_layout.clear()
        self.main_layout.append(self.loading_placeholder)
    
    def reset_visualization(self):
        """Reset the main area to show the placeholder"""
        self.main_layout.clear()
        self.main_layout.append(self.no_file_placeholder)
    
    def create_eels_visualization(self, dataset_type: str):
        """
        Create EELS visualization based on dataset type.
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate visualization
        """
        visualization_result = self.visualization_factory.create_visualization(dataset_type)
        
        # Store reference to current visualizer for interaction access
        self.current_visualizer = self.visualization_factory.current_visualizer
        
        return visualization_result
    
    @property
    def tap_stream(self):
        """Get tap stream from current visualizer"""
        if self.current_visualizer and hasattr(self.current_visualizer, 'tap_stream'):
            return self.current_visualizer.tap_stream
        return None
    
    @property
    def spectrum_pane(self):
        """Get spectrum pane from current visualizer"""
        if self.current_visualizer and hasattr(self.current_visualizer, 'spectrum_pane'):
            return self.current_visualizer.spectrum_pane
        return None