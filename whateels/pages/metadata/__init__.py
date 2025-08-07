from whateels.components import CustomPage
from .MVC import Model, Controller, View

class Metadata(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """

    def __init__(self, title: str = None):
        self.model = Model()
        self.view = View(self.model)
        self.controller = Controller(self.model, self.view)
        
        title = title or self.model.constants.TITLE
                
        super().__init__(
            title=title,
            main=[self.view.main],
            sidebar=[self.view.sidebar],
        )