from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from ..view import View

class Controller:
    """
    Controller for the metadata page.
    Simple coordinator between Model and View.
    """
    
    def __init__(self, model: "Model", view: "View") -> None:
        self._model = model
        self._view = view
