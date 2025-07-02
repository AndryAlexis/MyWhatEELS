import panel as pn
from whateels.components import CustomPage

class NLLS(CustomPage):
    """
    NLLS Page class for the WhatEELS application.
    This class extends CustomPage to create a specific NLLS page layout.
    """
    
    _DEFAULT_TITLE = "NLLS"
    
    def __init__(self, title: str = _DEFAULT_TITLE):
        super().__init__(
            title=title,
            right_sidebar=[pn.pane.Markdown("## NLLS Options")],
        )