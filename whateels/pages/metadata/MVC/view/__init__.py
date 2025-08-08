import panel as pn
import param
from typing import TYPE_CHECKING
from whateels.helpers.json_sanitizer import safe_json_dumps, is_json_serializable, sanitize_for_json

if TYPE_CHECKING:
    from ..model import Model

# Import AppState for reactive metadata access
from whateels.shared_state import AppState

class MetadataDisplayModel(param.Parameterized):
    """Parameterized model for reactive metadata display."""
    
    def __init__(self, **params):
        super().__init__(**params)
        self.app_state = AppState()
    
    @param.depends("app_state.metadata")
    def display(self):
        """Reactive display method that updates when metadata changes."""
        if self.app_state.is_metadata_available is False:
            # No metadata available
            with open('whateels/assets/html/no_metadata_loaded.html', 'r', encoding='utf-8') as f:
                no_metadata_template = f.read()
            return pn.pane.HTML(no_metadata_template, sizing_mode='stretch_both')
        
        try:
            # Always sanitize metadata first to ensure it's safe for JSON operations
            sanitized_metadata = sanitize_for_json(self.app_state.metadata)
            
            # Verify the sanitized metadata is truly JSON serializable
            if is_json_serializable(sanitized_metadata):
                # Use sanitized metadata in JSON pane
                return pn.Column(
                    pn.pane.JSON(
                        sanitized_metadata,
                        depth=1,  # Expand 1 level by default
                        hover_preview=True,  # Enable hover preview for collapsed nodes
                    ),
                    sizing_mode='stretch_both'
                )
            else:
                raise ValueError("Sanitized metadata is not JSON serializable")
                
        except Exception as e:
            # Show detailed error information using the styled error template
            with open('whateels/assets/html/json_error.html', 'r', encoding='utf-8') as f:
                error_template = f.read()
            return pn.pane.HTML(error_template)

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
            self.metadata_display.display,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout