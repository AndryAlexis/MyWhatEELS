import panel as pn
from typing import TYPE_CHECKING

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
        self._sidebar_container_layout = None
        
        self._init_components()
    
    # --- Properties ---
    
    @property
    def sidebar(self) -> pn.viewable.Viewable:
        """Sidebar layout containing metadata controls."""
        return self._sidebar_container_layout

    @property
    def main(self) -> pn.Column:
        """Main content area layout for displaying metadata."""
        return self._main_container_layout
        
    # --- Private/Internal Setup Methods ---
    
    def _init_components(self):
        """Initialize main and sidebar layout containers."""
        self._sidebar_container_layout = self._sidebar_layout()
        self._main_container_layout = self._main_layout()

    def _sidebar_layout(self):
        """Create and return the sidebar layout."""
        self._sidebar_container_layout = pn.Column(
            pn.pane.HTML("<h3>Metadata Controls</h3>"),
            pn.Spacer(height=10),
            sizing_mode=self._STRETCH_WIDTH
        )
        return self._sidebar_container_layout

    def _main_layout(self):
        """Create and return the main layout."""
        self._main_container_layout = pn.Column(
            pn.pane.HTML("<h2>Metadata Page</h2>"),
            pn.pane.HTML("<p>Display metadata information here.</p>"),
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout
