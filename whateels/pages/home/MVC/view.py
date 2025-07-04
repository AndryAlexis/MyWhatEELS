from .model import Model
import panel as pn
from whateels.components import FileDropper

class View:
    """
    View class for the home page of the WhatEELS application.
    This class is responsible for creating the layout and components of the home page.
    It uses the Model to access constants and configurations.
    """
    def __init__(self, model: Model):
        self.model = model
        self.callbacks = {} # Dictionary to hold callbacks
    
    def _sidebar_layout(self):
        """
        Create and return the sidebar layout for the view.
        """

        file_dropper = FileDropper(
            valid_extensions=Model.FileDropper.VALID_EXTENSIONS,
            reject_message=Model.FileDropper.REJECT_MESSAGE,
            success_message=Model.FileDropper.SUCCESS_MESSAGE,
            feedback_message=Model.FileDropper.FEEDBACK_MESSAGE,
            on_file_uploaded_callback=self.callbacks.get(Model.Callbacks.FILE_UPLOADED),
            on_file_removed_callback=self.callbacks.get(Model.Callbacks.FILE_REMOVED)
        )
        
        file_dropper_box = pn.WidgetBox(file_dropper)
        
        column = pn.Column(
            file_dropper_box,
            sizing_mode='stretch_width'
        )

        return column
    
    def _main_layout(self):
        default_content = pn.pane.Markdown("# Home Page")
        return default_content
    
    @property
    def sidebar(self) -> pn.WidgetBox:
        return self._sidebar_layout()
    
    @property
    def main(self):
        return self._main_layout()
    
    @property
    def callbacks(self) -> dict:
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, value : dict):
        if not isinstance(value, dict):
            raise ValueError("Callbacks must be a dictionary")
        self._callbacks = value