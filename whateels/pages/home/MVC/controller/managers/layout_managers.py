import panel as pn
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...view import View

class LayoutManager:
    """
    Manager class responsible for handling all layout operations in the WhatEELS application.
    
    This class encapsulates all UI layout management functionality, including:
    - Main layout state management (loading, error, content, placeholder states)
    - Sidebar component management
    - Float panel operations
    
    By separating layout concerns from the main Controller, we achieve better
    code organization and single responsibility principle.
    """
    
    def __init__(self, view: "View"):
        """
        Initialize the LayoutManager with a reference to the View.
        
        Args:
            view: The View instance that contains the UI components to manage
        """
        self.view = view
    
    def show_loading_placeholder_in_main_layout(self):
        """Show the loading placeholder in the main layout."""
        self.view.main.clear()
        self.view.main.append(self.view.loading_placeholder)
        
    def reset_main_layout(self):
        """Reset the main layout to the no-file placeholder."""
        self.view.main.clear()
        self.view.main.append(self.view.no_file_placeholder)

    def update_main_layout(self, plot_component):
        """Update the main layout with a new plot component."""
        self.view.main.clear()
        self.view.main.append(plot_component)
        
    def show_error_placeholder_in_main_layout(self):
        """Show the error placeholder in the main layout."""
        self.view.main.clear()
        self.view.main.append(self.view.error_placeholder)
        
    def add_component_to_sidebar_layout(self, component: pn.viewable.Viewable):
        """Add a component to the sidebar and track it as the last dataset info component."""
        self.view.sidebar.append(component)
        self.view.dataset_info = component
        
    def remove_dataset_info_from_sidebar(self):
        """Remove the last dataset info component from the sidebar, if present."""
        if self.view.dataset_info is None:
            return
        if self.view.dataset_info in self.view.sidebar:
            self.view.sidebar.remove(self.view.dataset_info)
            self.view.dataset_info = None