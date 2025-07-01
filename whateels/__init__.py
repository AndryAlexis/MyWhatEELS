import panel as pn
from whateels.pages import Home, NLLS, Login

class App():
    """
    Main application class for WhatEELS.
    
    This class initializes the Panel application with the necessary pages and configurations.
    """
    
    _DEFAULT_TITLE = "WhatEELS"
    
    def __init__(self, title : str = _DEFAULT_TITLE):
        self.title = title

    def run(self, port : int = 5006):
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