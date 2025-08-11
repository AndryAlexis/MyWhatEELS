from whateels.components import CustomPage
from .MVC import Model, Controller, View

class Metadata(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """

    def __init__(self, title: str = None):
        self.model = Model()
        self.view = View(self.model)  # Create view first
        self.controller = Controller(self.model, self.view)  # Pass view to controller
        
        title = title or self.model.constants.TITLE
                
        super().__init__(
            title=title,
            main=[self.view.main],
            header=[], # No header for metadata page, pass [] to avoid default header
            header_background="#0066cc"
        )