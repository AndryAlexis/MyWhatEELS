from whateels.components import CustomPage
from .MVC import Model, Controller, View

class Home(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """

    def __init__(self, title: str = None):
        model = Model()
        view = View(model)
        Controller(model, view)
        
        title = title or model.constants.TITLE
        
        super().__init__(
            title=title,
            main=[view.main],
            sidebar=[view.sidebar],
            on_load_page=self._testing_load_page
        )

    def _testing_load_page(self):
        print("Home page loaded successfully!")