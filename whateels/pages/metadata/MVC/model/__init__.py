from whateels.helpers.json_sanitizer import is_json_serializable, sanitize_for_json
from whateels.shared_state import AppState

class Model:
    """
    Model for the metadata page.
    Handles data and business logic for metadata information.
    """
    
    def __init__(self):
        self.app_state = AppState()
    
    def get_sanitized_metadata(self):
        """Returns sanitized metadata ready for display."""
        return sanitize_for_json(self.app_state.metadata)
    
    def is_metadata_serializable(self, data):
        """Check if data can be JSON serialized."""
        return is_json_serializable(data)
    
    def is_metadata_available(self) -> bool:
        """Check if metadata is available."""
        return self.app_state.is_metadata_available
    
    def get_metadata(self):
        """Get raw metadata."""
        return self.app_state.metadata

    @property
    def constants(self) -> "Constants":
        """Expose constants for the metadata page."""
        return self.Constants()

    class Constants:
        TITLE = "Eels Metadata Details"
