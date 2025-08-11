import param, panel as pn
from whateels.helpers.json_sanitizer import  is_json_serializable, sanitize_for_json
from whateels.shared_state import AppState

class MetadataDisplayModel(param.Parameterized):
    """Parameterized model for reactive metadata display."""
    
    def __init__(self, **params):
        super().__init__(**params)
        self.app_state = AppState()
    
    @param.depends("app_state.metadata")
    def refresh_display(self):
        """Reactive display method that updates when metadata changes."""
        if self.app_state.is_metadata_available is False:
            # No metadata available
            with open('whateels/assets/html/no_metadata_loaded.html', 'r', encoding='utf-8') as f:
                no_metadata_template = f.read()
            return pn.pane.HTML(no_metadata_template, sizing_mode='stretch_both')
        
        try:
            # Always sanitize metadata first to ensure it's safe for JSON operations
            sanitized_metadata = sanitize_for_json(self.app_state.metadata)
            
            # Verify the sanitized metadata is truly JSON serializable
            if is_json_serializable(sanitized_metadata):
                # Use sanitized metadata in JSON pane
                return pn.Column(
                    pn.pane.JSON(
                        sanitized_metadata,
                        depth=1,  # Expand 1 level by default
                        hover_preview=True,  # Enable hover preview for collapsed nodes
                    ),
                    sizing_mode='stretch_both'
                )
            else:
                raise ValueError("Sanitized metadata is not JSON serializable")
                
        except Exception as e:
            # Show detailed error information using the styled error template
            with open('whateels/assets/html/json_error.html', 'r', encoding='utf-8') as f:
                error_template = f.read()
            return pn.pane.HTML(error_template)
