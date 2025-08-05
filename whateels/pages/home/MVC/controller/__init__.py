import traceback

from .services import EELSFileProcessor, EELSDataProcessor
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
        
        # Initialize services
        self.file_service = EELSFileProcessor(model)
        self.data_service = EELSDataProcessor(self.model)
    
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
        self.show_loading_placeholder_in_main_layout()
        
        # Delegate to file service
        dataset = self.file_service.process_upload(filename, file_content)
        
        if dataset is None:
            # Reset to placeholder on error
            self.reset_main_layout()
            print(f'Error loading file: {filename}')
            return 

        # Set dataset in model
        self.model.dataset = dataset
        
        # Create EELS plots based on dataset type
        spectrum_plots_created, spectrum_dataset_info_created = self._create_eels_plot_and_dataset_info(self.model.dataset.attrs.get('dataset_type', None))

        # (No tap callback setup needed; handled in visualizer if required)
        
        # Update the view with the new plot
        self.update_main_layout(spectrum_plots_created)
        self.add_component_to_sidebar_layout(spectrum_dataset_info_created)

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
            self.show_error_placeholder_in_main_layout()
            return
        # Store the active plotter for interaction handling
        self.view.chosed_spectrum = chosed_spectrum
        spectrum_plots_created = chosed_spectrum.create_plots()
        spectrum_dataset_info_created = chosed_spectrum.create_dataset_info()

        return spectrum_plots_created, spectrum_dataset_info_created

    def show_loading_placeholder_in_main_layout(self):
        """Show the loading placeholder in the main layout."""
        self.view.main.clear()
        self.view.main.append(self.view.loading_placeholder)
        
    def reset_main_layout(self):
        """Reset the main layout to the no-file placeholder."""
        self.view.main.clear()
        self.view.main.append(self.view.no_file_placeholder)

    def update_main_layout(self, plot_component):
        """Update the main layout with a new plot component."""
        self.view.main.clear()
        self.view.main.append(plot_component)
        
    def show_error_placeholder_in_main_layout(self):
        """Show the error placeholder in the main layout."""
        self.view.main.clear()
        self.view.main.append(self.view.error_placeholder)
        
    def add_component_to_sidebar_layout(self, component: pn.viewable.Viewable):
        """Add a component to the sidebar and track it as the last dataset info component."""
        self.view.sidebar.append(component)
        self.view.last_dataset_info_component = component
        
    def remove_dataset_info_from_sidebar(self):
        """Remove the last dataset info component from the sidebar, if present."""
        if self.view.last_dataset_info_component is None:
            return
        if self.view.last_dataset_info_component in self.view.sidebar:
            self.view.sidebar.remove(self.view.last_dataset_info_component)
            self.view.last_dataset_info_component = None
            
    def toggle_float_panel(self):
        """
        Toggle the visibility of the float panel.
        If the panel is closed, open it with the current active plotter.
        If the panel is open, close it.
        """
        if self.view._float_panel.status == 'closed':
            if self.view.chosed_spectrum is not None:
                self.view._float_panel.content = self.view.chosed_spectrum.float_panel_content
            else:
                self.view._float_panel.content = pn.pane.HTML("No active plotter available.")
        self.view._float_panel.toggle()

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
        self.remove_dataset_info_from_sidebar()
        # Reset plot display to placeholder when file is removed
        self.reset_main_layout()
