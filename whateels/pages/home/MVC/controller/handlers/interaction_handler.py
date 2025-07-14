
"""
Interaction Handler for managing user interactions and UI updates.

This handler manages all user interaction operations including:
- Tap/click event processing
- Coordinate throttling and validation
- Spectrum display updates
- UI feedback updates
"""

import holoviews as hv

class InteractionHandler:
    """Handler class for managing user interactions"""
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # Add throttling for click events to prevent too frequent updates
        self._last_click_coords = (None, None)
        self._click_tolerance = 0.5  # Minimum distance to trigger update
    
    def setup_tap_callback(self, tap_stream):
        """Setup tap callback for interaction streams"""
        if tap_stream:
            tap_stream.add_subscriber(self._handle_tap_stream)
    
    def _handle_tap_stream(self, **kwargs):
        """Handle tap events from HoloViews streams"""
        # Extract x, y from stream parameters
        x = kwargs.get('x', None)
        y = kwargs.get('y', None)
        self.handle_tap_event(x, y)
    
    def handle_tap_event(self, x, y):
        """Handle tap events on the visualization"""
        # Only update if coordinates are valid
        if x is None or y is None:
            return
            
        if self.model.dataset is None:
            return
        
        # Throttle click events - only update if position changed significantly
        last_x, last_y = self._last_click_coords
        if (last_x is not None and last_y is not None and 
            abs(x - last_x) < self._click_tolerance and abs(y - last_y) < self._click_tolerance):
            return
            
        # Update last click coordinates
        self._last_click_coords = (x, y)
            
        try:
            if self.model.dataset_type == self.model.constants.SPECTRUM_IMAGE:
                self._handle_spectrum_image_click(x, y)
            elif self.model.dataset_type == self.model.constants.SPECTRUM_LINE:
                self._handle_spectrum_line_click(x, y)
        except Exception as e:
            # Don't print errors for click events as they happen frequently
            pass
    
    def _handle_spectrum_image_click(self, x, y):
        """Handle click on spectrum image"""
        # Get spectrum at clicked position
        spectrum = self.model.dataset.ElectronCount.sel(
            x=x, y=y, method='nearest'
        )
        
        # Update the spectrum visualization
        self.update_spectrum_display(spectrum)
        
        # Update click feedback
        click_text = self.model.constants.CLICK_TEXT_2D_TEMPLATE.format(int(x), int(y))
        if hasattr(self.view, 'click_feedback_widget') and self.view.click_feedback_widget:
            self.view.click_feedback_widget.value = click_text
    
    def _handle_spectrum_line_click(self, x, y):
        """Handle click on spectrum line"""
        # Get spectrum at clicked x position (y is not relevant for spectrum line)
        spectrum = self.model.dataset.ElectronCount.sel(
            x=x, method='nearest'
        )
        
        # Update the spectrum visualization
        self.update_spectrum_display(spectrum)
        
        # Update click feedback
        click_text = self.model.constants.CLICK_TEXT_1D_TEMPLATE.format(int(x))
        if hasattr(self.view, 'click_feedback_widget') and self.view.click_feedback_widget:
            self.view.click_feedback_widget.value = click_text
    
    def update_spectrum_display(self, spectrum_data):
        """Update the spectrum display with new data"""
        try:
            # Check if the view and spectrum pane are still valid
            if not hasattr(self.view, 'spectrum_pane') or self.view.spectrum_pane is None:
                return
                
            # Check if the spectrum pane object is still alive (not removed)
            if not hasattr(self.view.spectrum_pane, 'object'):
                return
            
            # Create new spectrum curve
            spectrum_curve = hv.Curve(
                spectrum_data,
                kdims=[self.model.constants.ELOSS],
                vdims=[self.model.constants.ELECTRON_COUNT]
            ).opts(
                width=600,
                height=400,
                color=self.model.colors.RED,
                line_width=2,
                xlabel='Energy Loss (eV)',
                ylabel='Electron Count',
                title='Selected Spectrum'
            )
            
            # Update the view's spectrum display safely
            try:
                self.view.spectrum_pane.object = spectrum_curve
            except Exception as update_error:
                # If update fails, the pane might have been removed - ignore silently
                pass
                
        except Exception as e:
            # Silently handle errors during spectrum updates
            pass
    
    def reset_click_state(self):
        """Reset click state (useful when files are uploaded/removed)"""
        self._last_click_coords = (None, None)
