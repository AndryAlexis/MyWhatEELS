import traceback

from .services import EELSFileProcessor, EELSDataProcessor
from .managers import LayoutManager
from .eels_plot_factory import EELSPlotFactory
import panel as pn

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from ..view import View

class Controller:
    """
    Controller class for the home page of the WhatEELS application.

    Responsibilities:
    - Orchestrate file upload and removal events
    - Coordinate between services (file processing, data processing, interaction handling)
    - Manage workflow and UI state transitions by instructing the View
    - Delegate business logic to specialized services
    """
    def __init__(self, model: "Model", view: "View"):
        self.model = model
        self.view = view
        
        # Set up callbacks for file dropper events
        self.view.file_dropper.on_file_uploaded_callback = self.handle_file_uploaded
        self.view.file_dropper.on_file_removed_callback = self.handle_file_removed
        
        # Initialize services and managers
        self.file_service = EELSFileProcessor(model)
        self.data_service = EELSDataProcessor(self.model)
        self.layout_manager = LayoutManager(view)
    
    def handle_file_uploaded(self, filename: str, file_content: bytes):
        """
        Handle file upload event from the FileDropper component.

        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file

        Workflow:
        - Show loading placeholder
        - Process file and update model
        - Create EELS plots and dataset info
        - Set up tap/click interaction callback if available
        - Update main layout and sidebar
        """
        # Show loading screen immediately
        self.layout_manager.show_loading_placeholder_in_main_layout()
        
        # Delegate to file service
        dataset = self.file_service.process_upload(filename, file_content)
        
        if dataset is None:
            # Reset to placeholder on error
            self.layout_manager.reset_main_layout()
            print(f'Error loading file: {filename}')
            return 

        # Set dataset in model
        self.model.dataset = dataset
        
        # Create EELS plots based on dataset type
        spectrum_plots_created, spectrum_dataset_info_created = self._create_eels_plot_and_dataset_info(self.model.dataset.attrs.get('dataset_type', None))

        # (No tap callback setup needed; handled in visualizer if required)
        
        # Update the view with the new plot
        self.layout_manager.update_main_layout(spectrum_plots_created)
        self.layout_manager.add_component_to_sidebar_layout(spectrum_dataset_info_created)

        print(f'Successfully loaded and visualized: {filename}')
        
    def _create_eels_plot_and_dataset_info(self, dataset_type: str):
        """
        Create EELS plots and dataset info component for the given dataset type.

        Args:
            dataset_type: Type of dataset (e.g., SSp, SLi, SIm)

        Returns:
            Tuple of (plot component, dataset info component), or None if error.
        """
        self.eels_plot_factory = EELSPlotFactory(self.model, self)
        chosed_spectrum = self.eels_plot_factory.choose_spectrum(dataset_type)
        if chosed_spectrum is None:
            traceback.print_exc()
            self.layout_manager.show_error_placeholder_in_main_layout()
            return
        # Store the active plotter for interaction handling
        self.view.chosed_spectrum = chosed_spectrum
        spectrum_plots_created = chosed_spectrum.create_plots()
        spectrum_dataset_info_created = chosed_spectrum.create_dataset_info()

        return spectrum_plots_created, spectrum_dataset_info_created

    def toggle_float_panel(self):
        """
        Toggle the visibility of the float panel.
        Delegates to the layout manager.
        """
        self.layout_manager.toggle_float_panel()

    def handle_file_removed(self, filename: str):
        """
        Handle file removal event from the FileDropper component.

        Args:
            filename: Name of the removed file

        Workflow:
        - Remove last dataset info from sidebar
        - Reset main layout to placeholder
        """
        print('File removed', filename)
        self.layout_manager.remove_dataset_info_from_sidebar()
        # Reset plot display to placeholder when file is removed
        self.layout_manager.reset_main_layout()
