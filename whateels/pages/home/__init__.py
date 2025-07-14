from whateels.components import CustomPage
from .MVC import Model, Controller, View

class Home(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """

    def __init__(self, title: str = None):
        self.model = Model()
        self.view = View(self.model)  # No callbacks yet
        self.controller = Controller(self.model, self.view)
        
        title = title or self.model.constants.TITLE
        
        # Setup callbacks after controller exists
        callbacks = {
            self.model.callbacks.FILE_UPLOADED : self.controller.handle_file_uploaded,
            self.model.callbacks.FILE_REMOVED : self.controller.handle_file_removed,
            # Add more callbacks as needed
        }
        self.view.callbacks = callbacks
        
        super().__init__(
            title=title,
            main=[self.view.main],
            sidebar=[self.view.sidebar],
        )