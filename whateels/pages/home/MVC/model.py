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
        LOADING_FILE = """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 8px">
                
                <!-- EELS Spectrum Animation -->
                <div style="position: relative; width: 200px; height: 100px; margin-bottom: 30px;">
                    <!-- Spectrum lines -->
                    <div class="spectrum-container">
                        <div class="spectrum-line" style="animation-delay: 0s;"></div>
                        <div class="spectrum-line" style="animation-delay: 0.2s;"></div>
                        <div class="spectrum-line" style="animation-delay: 0.4s;"></div>
                        <div class="spectrum-line" style="animation-delay: 0.6s;"></div>
                        <div class="spectrum-line" style="animation-delay: 0.8s;"></div>
                    </div>
                    
                    <!-- Scanning beam -->
                    <div class="scanning-beam"></div>
                </div>
                
                <!-- Loading text with electron icon -->
                <div style="text-align: center;">
                    <h3 style="color: #2c3e50; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 3rem;">
                        ⚛️ Processing EELS Data
                    </h3>
                    <p style="color: #7f8c8d; margin: 10px 0 0 0; font-size: 2rem;">
                        Analyzing electron energy loss spectrum...
                    </p>
                </div>
            </div>
            
            <style>
                .spectrum-container {
                    position: relative;
                    width: 200px;
                    height: 80px;
                    border-left: 2px solid #34495e;
                    border-bottom: 2px solid #34495e;
                }
                
                .spectrum-line {
                    position: absolute;
                    bottom: 0;
                    width: 5px;
                    background: linear-gradient(to top, #3498db, #2980b9);
                    border-radius: 2px 2px 0 0;
                    animation: spectrum-grow 2s ease-in-out infinite;
                }
                
                .spectrum-line:nth-child(1) { left: 20px; }
                .spectrum-line:nth-child(2) { left: 50px; }
                .spectrum-line:nth-child(3) { left: 80px; }
                .spectrum-line:nth-child(4) { left: 110px; }
                .spectrum-line:nth-child(5) { left: 140px; }
                
                .scanning-beam {
                    position: absolute;
                    top: -10px;
                    width: 3px;
                    height: 100px;
                    background: linear-gradient(to bottom, #e74c3c, transparent);
                    animation: scan-beam 3s linear infinite;
                }
                
                @keyframes spectrum-grow {
                    0%, 100% { height: 10px; opacity: 0.5; }
                    50% { height: 60px; opacity: 1; }
                }
                
                @keyframes scan-beam {
                    0% { left: 0px; opacity: 0; }
                    10% { opacity: 1; }
                    90% { opacity: 1; }
                    100% { left: 200px; opacity: 0; }
                }
                
                /* Pulsing glow effect */
                @keyframes glow-pulse {
                    0%, 100% { box-shadow: 0 0 5px #3498db; }
                    50% { box-shadow: 0 0 20px #3498db, 0 0 30px #3498db; }
                }
                
                .spectrum-container {
                    animation: glow-pulse 2s ease-in-out infinite;
                }
            </style>
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
    
    def set_dataset(self, dataset: xr.Dataset, dataset_type: str = None):
        """Set the dataset and its type"""
        self.dataset = dataset
        self.dataset_type = dataset_type