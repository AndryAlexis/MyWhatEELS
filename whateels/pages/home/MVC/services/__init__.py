"""
Services module for the Home page MVC architecture.

This module contains service classes that handle specific business logic
operations, keeping the main controller focused on orchestration.
"""

from .file_service import FileService
from .eels_data_processor import EELSDataProcessor

__all__ = ['FileService', 'EELSDataProcessor']
