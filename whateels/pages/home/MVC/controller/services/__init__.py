"""
Services module for the Home page MVC architecture.

This module contains service classes that handle specific business logic
operations, keeping the main controller focused on orchestration.
"""

from .eels_file_processor_service import EELSFileProcessorService
from .eels_data_processor_service import EELSDataProcessorService
from .file_operation_service import FileOperationService

__all__ = ['EELSFileProcessorService', 'EELSDataProcessorService', 'FileOperationService']