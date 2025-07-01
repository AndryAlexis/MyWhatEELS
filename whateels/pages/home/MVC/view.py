from .model import Model
import panel as pn
from whateels.components import file_dropper

class View:
    def __init__(self, model: Model):
        pass
    
    def _sidebar_layout(self):
        """
        Create and return the sidebar layout for the view.
        """
        fdw_box = pn.WidgetBox(
            file_dropper()
        )
        return fdw_box
    
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