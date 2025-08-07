"""
Shared Application State for WhatEELS

This module provides a singleton AppState class to manage shared metadata
across different pages and components of the WhatEELS application.

The AppState uses Python properties for clean, Pythonic access to shared data.
"""

from typing import Optional, Dict, Any
from .helpers.logging import Logger

_logger = Logger.get_logger("shared_state.log", __name__)


class AppState:
    """
    Singleton class for sharing metadata between pages in the WhatEELS application.
    
    This class provides a clean, Pythonic interface using properties to store and
    access EELS metadata across different pages without duplicating data.
    
    Attributes:
        metadata (Optional[Dict[str, Any]]): Dictionary containing EELS metadata
            or None if no data is loaded. Can also contain {'error': str} on errors.
        is_metadata_available (bool): Property that returns True if valid metadata
            is available (not None and no errors).
    
    Usage:
        # Store metadata (in home page after loading file):
        app_state = AppState()
        app_state.metadata = {
            'file_name': 'sample.dm4',
            'beam_energy_kev': 200.0,
            'convergence_angle_mrad': 25.0,
            # ... other metadata
        }
        
        # Access metadata (in any other page):
        app_state = AppState()  # Gets the same singleton instance
        if app_state.is_metadata_available:
            file_name = app_state.metadata['file_name']
            beam_energy = app_state.metadata['beam_energy_kev']
        
        # Clear metadata when needed:
        app_state.metadata = None
    
    Note:
        This is a singleton class - all instances of AppState() return the same object.
        Metadata persists across page navigation until explicitly cleared or overwritten.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metadata = None
        return cls._instance
    
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get the stored metadata.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing EELS metadata,
                None if no data loaded, or {'error': str} if extraction failed.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: Optional[Dict[str, Any]]):
        """
        Set the metadata.
        
        Args:
            value: Dictionary containing metadata, or None to clear.
                   Can be {'error': str} to indicate extraction errors.
        """
        self._metadata = value
        if value is not None:
            _logger.info(f"Metadata set")
        else:
            _logger.info("Metadata cleared")

    @property
    def is_metadata_available(self) -> bool:
        """
        Check if valid metadata is available.
        
        Returns:
            bool: True if metadata is a non-empty dict without errors,
                  False if metadata is None, contains errors, or is invalid.
        """
        return self._metadata is not None and isinstance(self._metadata, dict) and 'error' not in self._metadata