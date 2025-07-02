import panel as pn
import os

# Configure Panel with theme support (only called once here)
pn.extension('filedropper')

from whateels.helpers import LoadCSS
from whateels.pages import Home, NLLS, Login

class App():
    """
    Main application class for WhatEELS.
    
    This class initializes the Panel application with the necessary pages and configurations.
    """
    
    _DEFAULT_TITLE = "App"
    _DEFAULT_CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "css")
    
    def __init__(self, title : str = _DEFAULT_TITLE):
        self.title = title

    def run(self, port : int = 5006):
        # Load CSS files only once
        LoadCSS([
            f"{self._DEFAULT_CSS_PATH}/home.css",
            f"{self._DEFAULT_CSS_PATH}/login.css",
            f"{self._DEFAULT_CSS_PATH}/custom_page.css",
        ])
        # Define the pages for the application
        pages = {
            "/": Home(),
            "/nlls": NLLS(),
            "/login": Login(),
        }

        return pn.serve(
            pages,
            title=self.title,
            port=port,
        )