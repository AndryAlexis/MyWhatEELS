from .services import *
from .managers import LayoutManager
import numpy as np

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
        self._file_service = EELSFileProcessorService(model)
        self._data_service = EELSDataProcessorService(self.model)
        self._file_operation_service = FileOperationService(model, self)
        # Initialize manager
        self._layout_manager = LayoutManager(view)
        # Set up callbacks for file dropper events
        self.view.file_dropper.on_file_uploaded_callback = self._file_operation_service.handle_file_upload
        self.view.file_dropper.on_file_removed_callback = self._file_operation_service.handle_file_removal

    @property
    def layout(self) -> LayoutManager:
        """Expose the layout manager for external use."""
        return self._layout_manager

    @property
    def region_service(self) -> RegionExtractionService:
        """Expose the region extraction service for external use."""
        return RegionExtractionService

    @property
    def fitting_service(self) -> SpectrumFittingService:
        """Expose the fitting service for external use."""
        return SpectrumFittingService
    
    @property
    def spectrum_service(self) -> SpectrumExtractionService:
        """
        Returns a SpectrumExtractionService for the current dataset.
        """
        try:
            data_array = self.model.dataset.ElectronCount
            energy_axis = self.model.dataset.coords[self.model.constants.ELOSS].values
        except Exception as e:
            raise ValueError(f"Could not retrieve data_array or energy_axis from model: {e}")
        return SpectrumExtractionService(data_array, energy_axis)
