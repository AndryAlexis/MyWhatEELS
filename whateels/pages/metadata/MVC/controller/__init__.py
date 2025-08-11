import param
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from ..view import View

class Controller(param.Parameterized):
    """
    Controller for the metadata page.
    Coordinates between Model and View for metadata display.
    """
    
    def __init__(self, model: "Model", view: "View") -> None:
        super().__init__()
        self._model = model
        self._view = view
    
    @param.depends("_model.app_state.metadata")
    def get_display_component(self):
        """Determines what component to display based on metadata state."""
        if not self._model.is_metadata_available():
            return self._view.create_no_metadata_component()
        
        try:
            sanitized_metadata = self._model.get_sanitized_metadata()
            
            if self._model.is_metadata_serializable(sanitized_metadata):
                return self._view.create_json_component(sanitized_metadata)
            else:
                raise ValueError("Sanitized metadata is not JSON serializable")
                
        except Exception as e:
            return self._view.create_error_component()
