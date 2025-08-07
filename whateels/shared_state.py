"""
Shared Application State for WhatEELS

This module provides a singleton AppState class to manage shared metadata
across different pages and components of the WhatEELS application.
"""

from typing import Optional, Dict, Any, Union
from .helpers.parsers.dm_eels_data import DM_EELS_data
from .helpers.logging import Logger

_logger = Logger.get_logger("shared_state.log", __name__)


class AppState:
    """
    Simple singleton class to share metadata between pages.
    
    Usage:
        # In home page after loading file:
        app_state = AppState()
        app_state.metadata = extract_metadata(dm_eels_instance)
        
        # In any other page:
        app_state = AppState()  # Gets the same instance
        metadata = app_state.metadata
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metadata = None
        return cls._instance
    
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get the stored metadata."""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value: Optional[Dict[str, Any]]):
        """Set the metadata."""
        self._metadata = value
        if value is not None:
            _logger.info(f"Metadata set")
        else:
            _logger.info("Metadata cleared")
    
    @property
    def is_metadata_available(self) -> bool:
        """Check if metadata is available."""
        return self._metadata is not None and isinstance(self._metadata, dict) and 'error' not in self._metadata
    
    def clear_metadata(self):
        """Clear the stored metadata."""
        self.metadata = None
