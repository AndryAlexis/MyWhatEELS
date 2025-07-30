import traceback

from .services import EELSFileProcessor, EELSDataProcessor
from .handlers import InteractionHandler
from ..view.eels_plot_factory import EELSPlotFactory
import panel as pn

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from ..view import View

class Controller:
    """
    Controller class for the home page of the WhatEELS application.
    This class orchestrates file upload events and coordinates between services.
    It delegates specific operations to specialized services while maintaining
    the overall workflow coordination.
    """
    def __init__(self, model: "Model", view: "View"):
        self.model = model
        self.view = view
        
        # Set up callbacks for file dropper events
        self.view.file_dropper.on_file_uploaded_callback = self.handle_file_uploaded
        self.view.file_dropper.on_file_removed_callback = self.handle_file_removed
        
        # Initialize services
        self.file_service = EELSFileProcessor(model)
        self.data_service = EELSDataProcessor(self.model)
        self.interaction_handler = InteractionHandler(model, view)
    
    def handle_file_uploaded(self, filename: str, file_content: bytes):
        """
        🔽 FileDropper Event Handler: Handle file upload from the FileDropper component.
        
        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file
        """
        # Show loading screen immediately
        self.show_loading_placeholder_in_main_layout()
        
        # Delegate to file service
        dataset = self.file_service.process_upload(filename, file_content)
        
        if dataset is None:
            # Reset to placeholder on error
            self.interaction_handler.reset_click_state()
            self.reset_main_layout()
            print(f'Error loading file: {filename}')
            return 

        # Reset interaction state for new file
        self.interaction_handler.reset_click_state()
        
        # Set dataset in model with type from dataset metadata
        dataset_type = dataset.attrs.get('dataset_type', None)
        self.model.set_dataset(dataset, dataset_type)
        
        # Create EELS plots based on dataset type
        spectrum_plots_created, spectrum_dataset_info_created = self._create_eels_plot_and_dataset_info(dataset_type)

        # Setup interaction callbacks - use tap instead of hover
        if hasattr(self.view, 'tap_stream') and self.view.tap_stream:
            self.interaction_handler.setup_tap_callback(self.view.tap_stream)
        
        # Update the view with the new plot
        self.update_main_layout(spectrum_plots_created)
        self.add_component_to_sidebar_layout(spectrum_dataset_info_created)

        print(f'Successfully loaded and visualized: {filename}')
        
    def _create_eels_plot_and_dataset_info(self, dataset_type: str):
        """
        Create EELS plots based on dataset type.
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate plot visualization, or None
            if an error occurred (in which case the view will already show an error)
        """
        self.eels_plot_factory = EELSPlotFactory(self.model, self)
        chosed_spectrum = self.eels_plot_factory.choose_spectrum(dataset_type)
        if chosed_spectrum is None:
            traceback.print_exc()
            self.show_error_placeholder_in_main_layout()
            return
        # Store the active plotter for interaction handling
        self.view.active_plotter = chosed_spectrum
        spectrum_plots_created = chosed_spectrum.create_plots()
        spectrum_dataset_info_created = chosed_spectrum.create_dataset_info()

        return spectrum_plots_created, spectrum_dataset_info_created

    def show_loading_placeholder_in_main_layout(self):
        self.view.main.clear()
        self.view.main.append(self.view.loading_placeholder)
        
    def reset_main_layout(self):
        self.view.main.clear()
        self.view.main.append(self.view.no_file_placeholder)

    def update_main_layout(self, plot_component):
        self.view.main.clear()
        self.view.main.append(plot_component)
        
    def show_error_placeholder_in_main_layout(self):
        self.view.main.clear()
        self.view.main.append(self.view.error_placeholder)
        
    def add_component_to_sidebar_layout(self, component: pn.viewable.Viewable):
        self.view.sidebar.append(component)
        self.view.last_dataset_info_component = component
        
    def remove_last_dataset_info_from_sidebar(self):
        if self.view.last_dataset_info_component is None:
            return
        
        if self.view.last_dataset_info_component in self.view.sidebar:
            self.view.sidebar.remove(self.view.last_dataset_info_component)
            self.view.last_dataset_info_component = None

    def handle_file_removed(self, filename: str):
        """
        🔽 FileDropper Event Handler: Handle file removal from the FileDropper component.
        
        Args:
            filename: Name of the removed file
        """
        print('File removed', filename)
        
        # Reset interaction state
        self.interaction_handler.reset_click_state()
        
        self.remove_last_dataset_info_from_sidebar()
        
        # Reset plot display to placeholder when file is removed
        self.reset_main_layout()
