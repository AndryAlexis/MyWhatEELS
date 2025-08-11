import panel as pn
from typing import TYPE_CHECKING
from .metadata_display_model import MetadataDisplayModel

if TYPE_CHECKING:
    from ..model import Model

class View:
    """
    View class for the metadata page of the WhatEELS application.
    Handles the UI components and layout for displaying metadata information.
    """
    
    # --- Class-level constants ---
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'
    
    def __init__(self, model: "Model") -> None:
        self._model = model
        self._main_container_layout = None
        
        # Initialize metadata display
        self.metadata_display = MetadataDisplayModel()
        
        self._init_components()
    
    # --- Properties ---
    @property
    def main(self) -> pn.Column:
        """Main content area layout for displaying metadata."""
        return self._main_container_layout
        
    # --- Private/Internal Setup Methods ---
    
    def _init_components(self):
        """Initialize main and sidebar layout containers."""
        self._main_container_layout = self._main_layout()

    def _main_layout(self):
        """Create and return the main layout."""
        self._main_container_layout = pn.Column(
            self.metadata_display.refresh_display,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout