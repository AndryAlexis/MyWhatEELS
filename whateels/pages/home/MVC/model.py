from pathlib import Path
import xarray as xr
import numpy as np

class Model:
    """
    Model class for the home page of the WhatEELS application.
    This class contains constants and configurations used in the home page.
    """
    def __init__(self):
        self.dataset = None
        self.dataset_type = None
    
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

    class FileDropper:
        TITLE = "Upload EELS data file"
        VALID_EXTENSIONS = ('.dm3', '.dm4')
        REJECT_MESSAGE = "❌ File rejected - only EELS data files (.dm3/.dm4) are supported"
        SUCCESS_MESSAGE = "✅ Ready to analyze your EELS data"
        FEEDBACK_MESSAGE = "No file uploaded yet... :("

    class Callbacks:
        FILE_UPLOADED = "handle_file_uploaded",
        FILE_REMOVED = "handle_file_removed"
    
    class Placeholders:
        NO_FILE_LOADED = """
            <div style='width:100%; height:100%; background-color:#f5f5f5; 
                        display:flex; align-items:center; justify-content:center;
                        border:2px dashed #ccc; border-radius:8px; min-height:400px;'>
                <div style='text-align:center; color:#666;'>
                    <h3>No file loaded</h3>
                    <p>Upload a DM3 or DM4 file to see the visualization</p>
                </div>
            </div>
        """
    
    class Colors:
        """Color constants for visualization styling."""
        GREYS_R = 'Greys_r'
        GREY = 'grey'
        BLACK = 'black'
        WHITE = 'white'
        RED = 'red'
        LIMEGREEN = 'limegreen'
        DARKGREY = 'darkgrey'
        GHOSTWHITE = 'ghostwhite'
        ORANGERED = 'orangered'
        DARKRED = 'darkred'
    
    def set_dataset(self, dataset: xr.Dataset):
        """Set the dataset and determine its type"""
        self.dataset = dataset
        self.dataset_type = self._determine_dataset_type(dataset)
    
    def _determine_dataset_type(self, dataset: xr.Dataset) -> str:
        """Determine the type of dataset based on dimensions"""
        if len(dataset.coords[self.Constants.AXIS_X]) == 1 and len(dataset.coords[self.Constants.AXIS_Y]) == 1:
            return self.Constants.SINGLE_SPECTRUM
        elif len(dataset.coords[self.Constants.AXIS_Y]) == 1:
            return self.Constants.SPECTRUM_LINE
        else:
            return self.Constants.SPECTRUM_IMAGE