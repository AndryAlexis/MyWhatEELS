import panel as pn
pn.extension()

from whateels.components import file_dropper as fd

def home_main_area():    
    return pn.pane.Markdown("# Welcome to WhatEELS")

def home_sidebar_area():
    file_dropper, file_name_pane = fd()
    return pn.Column(
        file_dropper,
        file_name_pane,
        sizing_mode='stretch_width'
    )