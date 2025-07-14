"""
Services module for the Home page MVC architecture.

This module contains service classes that handle specific business logic
operations, keeping the main controller focused on orchestration.
"""

from .eels_file_processor import EELSFileProcessor
from .eels_data_processor import EELSDataProcessor

__all__ = ['EELSFileProcessor', 'EELSDataProcessor']