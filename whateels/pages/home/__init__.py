from whateels.components import CustomPage
from .MVC import Model, Controller, View

class Home(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """

    def __init__(self, title: str = Model.Constants.TITLE):
        self.model = Model()
        self.view = View(self.model)  # No callbacks yet
        self.controller = Controller(self.model, self.view)
        
        # Setup callbacks after controller exists
        callbacks = {
            self.model.Callbacks.FILE_UPLOADED : self.controller.handle_file_uploaded,
            self.model.Callbacks.FILE_REMOVED : self.controller.handle_file_removed,
            # Add more callbacks as needed
        }
        self.view.callbacks = callbacks
        
        super().__init__(
            title=title,
            main=[self.view.main],
            sidebar=[self.view.sidebar],
        )