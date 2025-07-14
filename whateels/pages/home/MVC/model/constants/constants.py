from pathlib import Path

class Constants:
    # Get the base directory of the current file
    # This assumes the structure is: whateels/pages/home/MVC/model.py
    CSS_PATH = Path(__file__).parent.parent.parent / "assets" / "css" / "home.css"
    TITLE = "WhatEELS"
    TEMP_PREFIX = "whateels_"
    
    # Visualization constants
    AXIS_X = 'x'
    AXIS_Y = 'y'
    ELOSS = 'Eloss'
    ELECTRON_COUNT = 'ElectronCount'
    CLICK_TEXT = 'click_text'

    # Dataset types
    SINGLE_SPECTRUM = 'SSp'
    SPECTRUM_LINE = 'SLi'
    SPECTRUM_IMAGE = 'SIm'
    
    # Click text templates
    CLICK_TEXT_1D_TEMPLATE = '|- y : {} -|'
    CLICK_TEXT_2D_TEMPLATE = '|- x : {} -|- y : {} -|'
    CLICK_TEXT_1D_NONE = '|- y : None -|'
    CLICK_TEXT_2D_NONE = '|- x : None -|- y : None -|'
    
    # None string
    NONE_TEXT = 'None'
