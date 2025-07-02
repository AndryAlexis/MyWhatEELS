from whateels.components import CustomPage
from .MVC import Model, Controller, View
from .MVC.model import *  # Import constants and other model components

class Home(CustomPage):
    """
    HomePage class for the WhatEELS application.
    This class extends CustomPage to create a specific home page layout.
    """
    
    def __init__(self, title: str = Constants.TITLE):
        
        # Phase 1: Create components without callbacks
        self.model = Model()
        self.view = View(self.model)  # No callbacks yet
        self.controller = Controller(self.model, self.view)
        
        # Setup callbacks after controller exists
        callbacks = {
            CALLBACKS.FILE_UPLOAD : self.controller.handle_file_upload,
            # Add more callbacks as needed
        }
        self.view.callbacks = callbacks
        
        super().__init__(
            title=title,
            main=[self.view.main],
            sidebar=[self.view.sidebar],
            raw_css_path=Constants.CSS_PATH,
        )