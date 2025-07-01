import panel as pn
pn.extension()

from whateels.components import CustomPage
from .MVC import Model, Controller, View
from .MVC.model import *  # Import constants and other model components

class Home(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """
    
    def __init__(self, title: str = Constants.TITLE):
        
        self.model = Model()
        self.view = View(self.model)
        self.controller = Controller(self.model, self.view)
        
        super().__init__(
            title=title,
            main=[self.view.main],
            sidebar=[self.view.sidebar],
            raw_css_path=Constants.CSS_PATH,
        )