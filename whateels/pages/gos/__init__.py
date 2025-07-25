import panel as pn
from whateels.components import CustomPage

class GOS(CustomPage):
    """
    GOS Page class for the WhatEELS application.
    This class extends CustomPage to create a specific GOS page layout.
    """
    
    _DEFAULT_TITLE = "GOS"
    
    def __init__(self, title: str = _DEFAULT_TITLE):
        super().__init__(
            title=title,
            right_sidebar=[pn.pane.Markdown("## GOS Options")],
        )