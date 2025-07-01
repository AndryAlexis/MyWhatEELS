"""
Controller layer for EELS visualization - handles user interactions and coordinates Model-View.
"""

import param
from typing import Optional

from .model import *
from .view import View


class Controller(param.Parameterized):
    """Coordinates user interactions between the Model and View layers."""
    
    click_text = param.String()
    
    def __init__(self, model: Model, view: View):
        """
        Initialize the controller.
        
        Args:
            model: Model object containing data and configuration
            view: View object for creating UI components
        """
        super().__init__()
        self.model = model
        self.view = view
        
        # Initialize click text based on dataset type
        self._initialize_click_text()
        
        # Setup UI components and interactions
        self._setup_visualization()
    
    def _initialize_click_text(self) -> None:
        """Initialize click text based on dataset type."""
        if self.model.dataset_type == Constants.SPECTRUM_LINE:
            self.click_text = Constants.CLICK_TEXT_1D_NONE
        elif self.model.dataset_type == Constants.SPECTRUM_IMAGE:
            self.click_text = Constants.CLICK_TEXT_2D_NONE
        else:
            self.click_text = ""
    
    def _setup_visualization(self) -> None:
        """Setup the appropriate visualization based on dataset type."""
        # Setup click feedback widget
        self.view.setup_click_feedback_widget(self)
        
        if self.model.dataset_type == Constants.SINGLE_SPECTRUM:
            self.view.create_single_spectrum_component()
            
        elif self.model.dataset_type == Constants.SPECTRUM_LINE:
            self.view.create_spectrum_line_components()
            self._setup_dynamic_interactions()
            
        elif self.model.dataset_type == Constants.SPECTRUM_IMAGE:
            self.view.create_spectrum_image_components()
            self._setup_dynamic_interactions()
    
    def _setup_dynamic_interactions(self) -> None:
        """Setup dynamic interactions for hover and tap events."""
        if self.model.dataset_type in [Constants.SPECTRUM_LINE, Constants.SPECTRUM_IMAGE]:
            spectrum_hover, spectrum_tap = self.view.create_dynamic_spectrum_maps(
                self._handle_hover_event,
                self._handle_tap_event
            )
            
            # Store references in view for layout creation
            self.view.spectrum_hover = spectrum_hover
            self.view.spectrum_tap = spectrum_tap
    
    def _handle_hover_event(self, x: float, y: float):
        """Handle hover events to preview spectrum."""
        return self.view.create_spectrum_visualization(x, y, is_tap=False)
    
    def _handle_tap_event(self, x: float, y: float):
        """Handle tap events to display selected spectrum."""
        if not self.model.is_point_in_bounds(x, y):
            # Update click text for out-of-bounds clicks
            if self.model.dataset_type == Constants.SPECTRUM_IMAGE:
                self.click_text = Constants.CLICK_TEXT_2D_TEMPLATE.format(Constants.NONE_TEXT, Constants.NONE_TEXT)
                return self.view.empty_spectrum
            elif self.model.dataset_type == Constants.SPECTRUM_LINE:
                self.click_text = Constants.CLICK_TEXT_1D_TEMPLATE.format(Constants.NONE_TEXT)
                return self.view.empty_curve
        else:
            # Update click text with coordinates
            if self.model.dataset_type == Constants.SPECTRUM_IMAGE:
                closest_x, closest_y = self.view.reference_image.closest((x, y))
                self.click_text = Constants.CLICK_TEXT_2D_TEMPLATE.format(str(int(closest_x)), str(int(closest_y)))
            elif self.model.dataset_type == Constants.SPECTRUM_LINE:
                closest_y = self.view.line_image.closest((x, y))[1]
                self.click_text = Constants.CLICK_TEXT_1D_TEMPLATE.format(str(int(closest_y)))
            
            return self.view.create_spectrum_visualization(x, y, is_tap=True)
