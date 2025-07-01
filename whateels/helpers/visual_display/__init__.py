"""
Visual Display Package - MVC Architecture

This package provides interactive visualizations for EELS (Electron Energy Loss Spectroscopy) data
using a Model-View-Controller (MVC) architecture for better maintainability and separation of concerns.
"""

import param  # For parameterized class properties and reactive programming
from .MVC import Model, View, Controller
from .MVC.model import *  # For constants

class VisualDisplay(param.Parameterized):
    """
    Main facade class for EELS data visualization using MVC architecture.
    """

    click_text = param.String()

    def __init__(self, dataset):
        """
        Initialize the visual display with a dataset.
        
        Args:
            dataset: xarray Dataset containing EELS data with dimensions x, y, and Eloss
        """
        super().__init__()
        
        # Initialize MVC components
        self.model = Model(dataset)
        self.view = View(self.model)
        self.controller = Controller(self.model, self.view)
        
        # Link click text to controller
        self.param.click_text = self.controller.param.click_text
    
    def create_panels(self):
        """Create and return the complete panel layout for visualization."""
        return self.view.create_panel_layout(
            self.model.dataset_type, 
            self.view.click_feedback_widget
        )
    
    @property
    def struc(self):
        return self.view.create_panel_layout(
            self.model.dataset_type, 
            self.view.click_feedback_widget
        )
    
    @property
    def panel_structure(self):
        return self.view.create_panel_layout(
            self.model.dataset_type, 
            self.view.click_feedback_widget
        )
    
    @property
    def dataset(self):
        return self.model.dataset
    
    @property
    def dataset_type(self):
        return self.model.dataset_type
    
    @property
    def empty_curve_dataset(self):
        return self.model.empty_curve_dataset


# Export classes and components
__all__ = [
    'VisualDisplay', 
    'Model', 'View', 'Controller',
    'Constants', 'Colors', 'Formatters', 'UIConfig'
]
