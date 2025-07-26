from ..model import Model
from ..view import View
from .services import EELSFileProcessor, EELSDataProcessor
from .handlers import InteractionHandler

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
        self.view.show_loading()
        
        # Delegate to file service
        dataset = self.file_service.process_upload(filename, file_content)
        
        if dataset is None:
            # Reset to placeholder on error
            self.interaction_handler.reset_click_state()
            self.view.reset_main_layout()
            print(f'Error loading file: {filename}')
            return 

        # Reset interaction state for new file
        self.interaction_handler.reset_click_state()
        
        # Set dataset in model with type from dataset metadata
        dataset_type = dataset.attrs.get('dataset_type', None)
        self.model.set_dataset(dataset, dataset_type)
        
        # Create plot based on dataset type
        eels_plots = self.view.create_eels_plot(self.model.dataset_type)
        
        # If plots creation failed, view already shows error so we're done
        if eels_plots is None:
            print(f'Error visualizing file: {filename}')
            return
            
        # Setup interaction callbacks - use tap instead of hover
        if hasattr(self.view, 'tap_stream') and self.view.tap_stream:
            self.interaction_handler.setup_tap_callback(self.view.tap_stream)
        
        # Update the view with the new plot
        self.view.update_main_layout(eels_plots)
        print(f'Successfully loaded and visualized: {filename}')

    def handle_file_removed(self, filename: str):
        """
        🔽 FileDropper Event Handler: Handle file removal from the FileDropper component.
        
        Args:
            filename: Name of the removed file
        """
        print('File removed', filename)
        
        # Reset interaction state
        self.interaction_handler.reset_click_state()
        
        # Reset plot display to placeholder when file is removed
        self.view.reset_main_layout()
        # Limpiar información de datos del sidebar cuando se elimina el archivo
        try:
            self.view._dataset_info_pane.clear()
        except Exception:
            pass
