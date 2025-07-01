"""
MVC Package - Model-View-Controller Architecture for EELS Visualization

This package contains the MVC components for EELS data visualization:
- Model: State management and data logic
- View: UI components and visualization
- Controller: Event handling and coordination
"""

# Import all MVC components
from .model import Model, Constants, Colors, Formatters, UIConfig
from .view import View
from .controller import Controller

# Export all components for easy importing
__all__ = [
    'Model', 'View', 'Controller',
    'Constants', 'Colors', 'Formatters', 'UIConfig'
]