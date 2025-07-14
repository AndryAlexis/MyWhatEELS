"""
FloatPanel Component

A custom floating panel component that extends Panel's built-in FloatPanel
with additional functionality and easier configuration.
"""

import panel as pn

class FloatPanel(pn.layout.FloatPanel):
    """
    Enhanced FloatPanel component that extends Panel's FloatPanel.
    
    This component adds:
    - Easy creation of a toggle button
    - Simplified visibility management
    - Default styling and configuration
    
    Usage:
        # Create a basic panel
        float_panel = FloatPanel(
            pn.pane.Markdown("# My Content"),
            name="My Panel"
        )
        
        # Create a panel with a toggle button
        toggle_button = float_panel.create_toggle_button("Toggle Panel")
        
        # Add to layout
        layout = pn.Column(toggle_button, float_panel)
    """
    
    def __init__(self, *objects, **params):
        # Default parameters that can be overridden
        default_params = {
            'position': 'center',
            'width': 400,
            'height': 300,
            'margin': 10,
            'theme': 'primary',
            'config': {
                "resizeit": {"handles": ["n", "e", "s", "w", "ne", "se", "sw", "nw"]},
            }
        }
        
        # Update defaults with any provided params
        for key, value in default_params.items():
            if key not in params:
                params[key] = value
                
        # Initialize the parent FloatPanel
        super().__init__(*objects, **params)
        
        # Initialize toggle button to None
        self._toggle_button = None
    
    def create_toggle_button(self, name='Toggle Panel', button_type='primary', width=150):
        """
        Create a button that toggles this panel's visibility
        
        Args:
            name (str): Label for the button
            button_type (str): Button style ('primary', 'success', etc.)
            width (int): Width of the button in pixels
            
        Returns:
            panel.widgets.Button: The created toggle button
        """
        self._toggle_button = pn.widgets.Button(
            name=name,
            button_type=button_type,
            width=width
        )
        self._toggle_button.on_click(self.toggle_visibility)
        return self._toggle_button
        
    def toggle_visibility(self, event=None):
        """
        Toggle between visible and hidden states
        
        Args:
            event: Button click event (optional)
        """
        # If closed, normalize. If normalized, close.
        if self.status == 'closed':
            self.status = 'normalized'
        else:
            self.status = 'closed'
    
    def show(self):
        """Make the panel visible by setting status to 'normalized'"""
        self.status = 'normalized'
        
    def hide(self):
        """Hide the panel by setting status to 'closed'"""
        self.status = 'closed'
    
    def is_visible(self):
        """Check if the panel is currently visible
        
        Returns:
            bool: True if visible, False if closed
        """
        return self.status != 'closed'
    
    @property
    def toggle_button(self):
        """
        Get the toggle button or create one if it doesn't exist
        
        Returns:
            panel.widgets.Button: The toggle button
        """
        if self._toggle_button is None:
            self._toggle_button = self.create_toggle_button()
        return self._toggle_button
