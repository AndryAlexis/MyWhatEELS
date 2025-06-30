"""
Visual Display Package - MVC Architecture

This package provides interactive visualizations for EELS (Electron Energy Loss Spectroscopy) data
using a Model-View-Controller (MVC) architecture for better maintainability and separation of concerns.
"""

import param
from .MVC import State, View, Controller
from .MVC.model import *  # For constants


class VisualDisplay(param.Parameterized):
    """
    Main facade class that maintains backward compatibility while using MVC architecture internally.
    
    This class serves as a wrapper around the MVC components, providing the same interface
    as the original VisualDisplay class while benefiting from the improved architecture.
    """
    click_text = param.String()

    def __init__(self, dataset):
        """
        Initialize the visual display with a dataset.
        
        Args:
            dataset: xarray Dataset containing EELS data with dimensions x, y, and Eloss
        """
        super().__init__()
        
        # Initialize MVC components using the existing architecture
        
        # Create the state (model) object
        self.state = State(dataset)
        
        # Create the view
        self.view = View(self.state)
        
        # Create the controller
        self.controller = Controller(self.state, self.view)
        
        # Link click text to controller for backward compatibility
        self.param.click_text = self.controller.param.click_text
    
    def create_panels(self):
        """Create the panel layout - maintained for backward compatibility."""
        return self.controller.create_panel_layout()
    
    @property
    def struc(self):
        """
        Backward compatibility property for the old 'struc' attribute name.
        Returns the panel structure.
        """
        return self.controller.panel_structure
    
    @property
    def panel_structure(self):
        """Access to the panel structure."""
        return self.controller.panel_structure
    
    # Expose commonly used attributes for backward compatibility
    @property
    def dataset(self):
        """Access to the dataset."""
        return self.state.dataset
    
    @property
    def dataset_type(self):
        """Access to the dataset type."""
        return self.state.dataset_type
    
    @property
    def empty_curve_dataset(self):
        """Access to the empty curve dataset."""
        return self.state.empty_curve_dataset


# Export the main class and MVC components
__all__ = [
    'VisualDisplay', 
    'State', 'View', 'Controller',
    'Constants', 'Colors', 'Formatters', 'UIConfig'
]
