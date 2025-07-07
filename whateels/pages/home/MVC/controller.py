from .model import Model
from .view import View
from .services import FileService, EELSDataProcessor
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
        self.file_service = FileService(model)
        self.data_service = EELSDataProcessor()
        self.interaction_handler = InteractionHandler(model, view)
    
    # ============================================================================
    # FileDropper Event Handlers
    # ============================================================================
    
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
        
        if dataset is not None:
            # Reset interaction state for new file
            self.interaction_handler.reset_click_state()
            
            # Set dataset in model
            self.model.set_dataset(dataset)
            
            # Create visualization based on dataset type
            visualization_component = self.view.create_eels_visualization(self.model.dataset_type)
            
            # Setup interaction callbacks - use tap instead of hover
            if hasattr(self.view, 'tap_stream') and self.view.tap_stream:
                self.interaction_handler.setup_tap_callback(self.view.tap_stream)
            
            # Update the view with the new visualization
            self.view.update_visualization(visualization_component)
            print(f'Successfully loaded and visualized: {filename}')
        else:
            # Reset to placeholder on error
            self.interaction_handler.reset_click_state()
            self.view.reset_visualization()
            print(f'Error loading file: {filename}')

    def handle_file_removed(self, filename: str):
        """
        🔽 FileDropper Event Handler: Handle file removal from the FileDropper component.
        
        Args:
            filename: Name of the removed file
        """
        print('File removed', filename)
        
        # Reset interaction state
        self.interaction_handler.reset_click_state()
        
        # Reset visualization to placeholder when file is removed
        self.view.reset_visualization()
        