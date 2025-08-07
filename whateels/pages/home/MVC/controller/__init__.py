from .services import EELSFileProcessor, EELSDataProcessor, FileOperation
from .managers import LayoutManager
from .dm_file_processing import DM_EELS_Reader, DM_InfoParser, DM_EELS_data

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
        
        # Initialize services
        self._file_service = EELSFileProcessor(model)
        self._data_service = EELSDataProcessor(self.model)
        self._file_operation_service = FileOperation(model, self)
        
        # Initialize manager
        self._layout_manager = LayoutManager(view)
        
        # Set up callbacks for file dropper events
        self.view.file_dropper.on_file_uploaded_callback = self._file_operation_service.handle_file_upload
        self.view.file_dropper.on_file_removed_callback = self._file_operation_service.handle_file_removal

    @property
    def layout(self) -> LayoutManager:
        """Expose the layout manager for external use."""
        return self._layout_manager
