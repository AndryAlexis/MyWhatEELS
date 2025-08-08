import panel as pn
import param
import json
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model

# Import AppState for reactive metadata access
from whateels.shared_state import AppState

class MetadataDisplayModel(param.Parameterized):
    """Parameterized model for reactive metadata display."""
    
    def __init__(self, **params):
        super().__init__(**params)
        self.app_state = AppState()
    
    def _sanitize_for_json(self, obj):
        """Convert all non-JSON serializable objects to strings."""
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, bool, type(None))):
            # For strings, ensure they don't contain problematic characters
            if isinstance(obj, str):
                try:
                    # Test if the string is JSON serializable
                    json.dumps(obj)
                    return obj
                except (UnicodeDecodeError, UnicodeEncodeError, TypeError):
                    # Replace problematic characters
                    return repr(obj)  # This will escape problematic characters
            return obj
        elif isinstance(obj, float):
            # Handle special float values that aren't valid JSON
            if np.isnan(obj):
                return "NaN"
            elif np.isinf(obj):
                return "Infinity" if obj > 0 else "-Infinity"
            else:
                return obj
        else:
            # Convert everything else to a safe string representation
            try:
                return str(obj)
            except:
                return f"<{type(obj).__name__}>"
    
    def _debug_json_error(self, sanitized_metadata):
        """Debug function to find what's causing JSON parse errors."""
        try:
            json_str = json.dumps(sanitized_metadata)
            print(f"JSON string length: {len(json_str)}")
            
            # Check around position 156284
            error_pos = 156284
            if len(json_str) > error_pos:
                start = max(0, error_pos - 50)
                end = min(len(json_str), error_pos + 50)
                problematic_section = json_str[start:end]
                print(f"Content around position {error_pos}: {repr(problematic_section)}")
                print(f"Character at position {error_pos}: {repr(json_str[error_pos])}")
            
            return json_str
        except Exception as e:
            print(f"JSON serialization error: {e}")
            return None
    
    @param.depends("app_state.metadata")
    def display(self):
        """Reactive display method that updates when metadata changes."""
        if self.app_state.is_metadata_available:
            try:
                # Sanitize metadata by converting non-JSON types to strings
                sanitized_metadata = self._sanitize_for_json(self.app_state.metadata)
                
                # Debug: Check what's causing the JSON error
                debug_result = self._debug_json_error(sanitized_metadata)
                
                # Use Panel's JSON pane for clean, interactive metadata display
                return pn.Column(
                    pn.pane.JSON(
                        sanitized_metadata,
                        depth=2,  # Expand 2 levels by default
                        hover_preview=True,  # Enable hover preview for collapsed nodes
                        height=400,  # Set a reasonable height
                        sizing_mode='stretch_width'
                    ),
                    sizing_mode='stretch_width'
                )
            except Exception as e:
                # Show detailed error information
                return pn.pane.HTML(
                    f"<div style='padding: 20px; background-color: #f8d7da; border-radius: 8px; border: 1px solid #f5c6cb;'>"
                    f"<h3 style='color: #721c24; margin-top: 0;'>Metadata Display Error</h3>"
                    f"<p style='color: #721c24; margin-bottom: 10px;'>Error: {str(e)}</p>"
                    f"<p style='color: #721c24; margin-bottom: 0;'>Check the console for debugging information.</p>"
                    f"</div>"
                )
        elif self.app_state.metadata is not None and 'error' in self.app_state.metadata:
            # Show error message
            error_msg = self.app_state.metadata['error']
            return pn.pane.HTML(
                f"<div style='padding: 20px; background-color: #f8d7da; border-radius: 8px; border: 1px solid #f5c6cb;'>"
                f"<h3 style='color: #721c24; margin-top: 0;'>Metadata Error</h3>"
                f"<p style='color: #721c24; margin-bottom: 0;'>{error_msg}</p>"
                f"</div>"
            )
        else:
            # No metadata available
            return pn.pane.HTML(
                f"<div style='padding: 20px; background-color: #d1ecf1; border-radius: 8px; border: 1px solid #bee5eb;'>"
                f"<h3 style='color: #0c5460; margin-top: 0;'>No Metadata Available</h3>"
                f"<p style='color: #0c5460; margin-bottom: 0;'>Load a file to view its metadata information.</p>"
                f"</div>"
            )

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

    def _sidebar_layout(self):
        """Create and return the sidebar layout."""
        return pn.Column(
            pn.pane.HTML("<h3>Metadata Controls</h3>"),
            pn.Spacer(height=10),
            sizing_mode=self._STRETCH_WIDTH
        )

    def _main_layout(self):
        """Create and return the main layout."""
        self._main_container_layout = pn.Column(
            self.metadata_display.display,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout