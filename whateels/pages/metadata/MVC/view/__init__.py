import panel as pn
from typing import TYPE_CHECKING
from pathlib import Path
from whateels.helpers import HTML_ROOT

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
        self._controller = None  # Will be set by the main page
        
        self._init_components()
    
    def set_controller(self, controller):
        """Set the controller reference for reactive display."""
        self._controller = controller
        self._update_layout()  # Update layout immediately when controller is set
    
    # --- UI Component Creation Methods ---
    
    def create_json_component(self, data):
        """Creates interactive JSON pane."""
        return pn.pane.JSON(
            data,
            depth=1,
            hover_preview=True,
            sizing_mode='stretch_both'
        )
    
    def create_no_metadata_component(self):
        """Creates no metadata available component."""
        with open(HTML_ROOT / "no_metadata_loaded.html", 'r', encoding='utf-8') as f:
            no_metadata_template = f.read()
        return pn.pane.HTML(no_metadata_template, sizing_mode='stretch_both')
    
    def create_error_component(self):
        """Creates error display component."""
        with open(HTML_ROOT / "json_error.html", 'r', encoding='utf-8') as f:
            error_template = f.read()
        return pn.pane.HTML(error_template, sizing_mode='stretch_both')
    
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
        # Create a placeholder that will be updated when controller is set
        self._main_container_layout = pn.Column(
            pn.pane.HTML("<p>Initializing...</p>"),
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout
    
    def _update_layout(self):
        """Update the layout with the controller's display component."""
        if self._controller and self._main_container_layout:
            # Clear and update the layout with the reactive component
            self._main_container_layout.clear()
            self._main_container_layout.append(self._controller.get_display_component)