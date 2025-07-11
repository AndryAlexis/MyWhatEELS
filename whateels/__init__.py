import panel as pn
from pathlib import Path

# Configure Panel with theme support (only called once here)
pn.extension('filedropper', 'floatpanel', theme='default')

from whateels.helpers import LoadCSS
from whateels.pages import Home, NLLS, Login

class App:
    """
    Main application class for WhatEELS.
    
    This class initializes the Panel application with the necessary pages and configurations.
    """

    _DEFAULT_TITLE = "App"
    _DEFAULT_PORT = 5006
    _DEFAULT_CSS_PATH = Path(__file__).parent / "assets" / "css"
    
    def __init__(self, title : str = _DEFAULT_TITLE):
        self.title = title

    def run(self, port : int = _DEFAULT_PORT):
        # Load CSS files only once
        LoadCSS([
            str(self._DEFAULT_CSS_PATH / "home.css"),
            str(self._DEFAULT_CSS_PATH / "login.css"),
            str(self._DEFAULT_CSS_PATH / "custom_page.css"),
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