from .model import Model, FILE_DROPPER, CALLBACKS
import panel as pn
from whateels.components import FileDropper

class View:
    def __init__(self, model: Model):
        self.model = model
        self.callbacks = {} # Dictionary to hold callbacks
    
    def _sidebar_layout(self):
        """
        Create and return the sidebar layout for the view.
        """
        
        file_dropper = FileDropper(
            valid_extensions=FILE_DROPPER.VALID_EXTENSIONS,
            reject_message=FILE_DROPPER.REJECT_MESSAGE,
            success_message=FILE_DROPPER.SUCCESS_MESSAGE,
            feedback_message=FILE_DROPPER.FEEDBACK_MESSAGE,
            callback_function=self.callbacks.get(CALLBACKS.FILE_UPLOAD)  # Get callback by name
        )
        
        file_dropper_box = pn.WidgetBox(file_dropper)

        return file_dropper_box
    
    def _main_layout(self):
        """
        Create and return the main layout for the view.
        """
        default_content = pn.pane.Markdown("# Home Page")
        return default_content
    
    @property
    def sidebar(self):
        """
        Property to access the sidebar layout.
        """
        return self._sidebar_layout()
    
    @property
    def main(self):
        """
        Property to access the main layout.
        """
        return self._main_layout()