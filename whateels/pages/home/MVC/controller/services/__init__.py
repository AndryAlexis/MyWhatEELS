"""
Services module for the Home page MVC architecture.

This module contains service classes that handle specific business logic
operations, keeping the main controller focused on orchestration.
"""

from .eels_file_processor import EELSFileProcessor
from .eels_data_processor import EELSDataProcessor
from .file_operation import FileOperation
from .region_extraction_service import RegionExtractionService
from .spectrum_extraction_service import SpectrumExtractionService
from .spectrum_fitting_service import SpectrumFittingService

__all__ = ['EELSFileProcessor', 'EELSDataProcessor', 'FileOperation', 'RegionExtractionService', 'SpectrumExtractionService', 'SpectrumFittingService']