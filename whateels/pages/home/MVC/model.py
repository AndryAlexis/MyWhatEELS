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
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed rgb(172, 172, 172); height: 100%; border-radius: 8px; min-height: 400px;">
                
                <!-- Empty EELS Visualization Animation -->
                <div style="position: relative; width: 200px; height: 120px; margin-bottom: 30px;">
                    <!-- Empty spectrum container -->
                    <div class="empty-spectrum-container">
                        <div class="empty-spectrum-axis-x"></div>
                        <div class="empty-spectrum-axis-y"></div>
                        
                        <!-- Upload arrow removed -->
                        
                        <!-- Dotted outline for spectrum -->
                        <div class="dotted-spectrum">
                            <svg width="100%" height="80px" style="position: absolute; bottom: 0; left: 0;">
                                <path class="animated-path" d="M20,80 Q40,40 60,60 T100,30 T140,50" 
                                      stroke="rgb(172, 172, 172)" stroke-width="3" fill="none"/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <!-- No File Text -->
                <div style="text-align: center;">
                    <h3 style="color: #2c3e50; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 2.2rem;">
                        No EELS Data Loaded
                    </h3>
                    <p style="color: #7f8c8d; margin: 10px 0 0 0; font-size: 1.3rem;">
                        Upload a DM3 or DM4 file to get started
                    </p>
                    <div class="upload-instruction">
                        <span class="upload-icon">📁</span>
                        <span class="chart-icon">📊</span>
                        <span class="data-icon">📈</span>
                    </div>
                </div>
            </div>
            
            <style>
                .empty-spectrum-container {
                    position: relative;
                    width: 200px;
                    height: 120px;
                    border-left: 2px dashed rgb(172, 172, 172);
                    border-bottom: 2px dashed rgb(172, 172, 172);
                    box-shadow: 0 0 10px rgba(172, 172, 172, 0.2);
                    overflow: hidden;
                }
                
                .empty-spectrum-axis-x {
                    position: absolute;
                    bottom: -2px;
                    left: 0;
                    width: 100%;
                    height: 2px;
                    background-color: rgb(172, 172, 172);
                    opacity: 0.5;
                }
                
                .empty-spectrum-axis-y {
                    position: absolute;
                    bottom: 0;
                    left: -2px;
                    width: 2px;
                    height: 100%;
                    background-color: rgb(172, 172, 172);
                    opacity: 0.5;
                }
                
                /* Upload arrow styles removed */
                
                .upload-instruction {
                    margin-top: 15px;
                    font-size: 2rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                }
                
                .upload-icon {
                    animation: slide-up 5s ease-in-out infinite;
                }
                
                .chart-icon {
                    animation: slide-up 5s ease-in-out infinite;
                    animation-delay: .5s; /* Offset the animation timing for wave effect */
                }
                
                .data-icon {
                    animation: slide-up 5s ease-in-out infinite;
                    animation-delay: 1s; /* Further offset for third icon in wave */
                }
                
                /* Animation for the dotted spectrum path */
                .animated-path {
                    animation: draw-erase 8s ease-in-out infinite;
                    stroke-dasharray: 200;
                    stroke-dashoffset: 200;
                }
                
                @keyframes draw-erase {
                    0% {
                        stroke-dashoffset: 200;
                    }
                    45% {
                        stroke-dashoffset: 0;
                    }
                    55% {
                        stroke-dashoffset: 0;
                    }
                    100% {
                        stroke-dashoffset: -200;
                    }
                }
                
                /* Smooth slide up animation with wave effect */
                
                @keyframes slide-up {
                    0% { 
                        transform: translateY(5px); 
                    }
                    50% { 
                        transform: translateY(-5px); 
                    }
                    100% {
                        transform: translateY(5px);
                    }
                }
            </style>
        """
        LOADING_FILE = """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; border-radius: 8px">
                
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
                    <h3 style="color: #2c3e50; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 2.2rem;">
                        ⚛️ Processing EELS Data
                    </h3>
                    <p style="color: #7f8c8d; margin: 10px 0 0 0; font-size: 1.3rem;">
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

        ERROR_FILE = """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; 
                        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%); border-radius: 8px; min-height: 400px;">
                
                <!-- EELS Error Animation -->
                <div style="position: relative; width: 200px; height: 120px; margin-bottom: 30px;">
                    <!-- Broken Spectrum Visualization -->
                    <div class="broken-spectrum-container">
                        <div class="broken-spectrum-axis-x"></div>
                        <div class="broken-spectrum-axis-y"></div>
                        
                        <!-- Broken spectrum pieces -->
                        <div class="broken-spectrum-piece" style="left: 20px; animation-delay: 0s;"></div>
                        <div class="broken-spectrum-piece" style="left: 60px; animation-delay: 0.2s;"></div>
                        <div class="broken-spectrum-piece" style="left: 100px; animation-delay: 0.4s;"></div>
                        <div class="broken-spectrum-piece" style="left: 140px; animation-delay: 0.6s;"></div>
                        
                        <!-- Error flash -->
                        <div class="error-flash"></div>
                        
                        <!-- Error icon -->
                        <div class="error-icon">⚠️</div>
                    </div>
                </div>
                
                <!-- Error text -->
                <div style="text-align: center;">
                    <h3 style="color: #c0392b; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 2.2rem;">
                        EELS Plot Error
                    </h3>
                    <p style="color: #7f8c8d; margin: 10px 0 0 0; font-size: 1.3rem;">
                        Could not process the EELS data
                    </p>
                    <p style="color: #e74c3c; margin: 10px 0 0 0; font-size: 1.1rem;" class="blink-text">
                        Please check the file format and try again
                    </p>
                </div>
            </div>
            
            <style>
                .broken-spectrum-container {
                    position: relative;
                    width: 200px;
                    height: 120px;
                    border-left: 2px solid #e74c3c;
                    border-bottom: 2px solid #e74c3c;
                    box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
                }
                
                .broken-spectrum-axis-x {
                    position: absolute;
                    bottom: -2px;
                    left: 0;
                    width: 100%;
                    height: 2px;
                    background-color: #e74c3c;
                }
                
                .broken-spectrum-axis-y {
                    position: absolute;
                    bottom: 0;
                    left: -2px;
                    width: 2px;
                    height: 100%;
                    background-color: #e74c3c;
                }
                
                .broken-spectrum-piece {
                    position: absolute;
                    bottom: 0;
                    width: 5px;
                    background: linear-gradient(to top, #e74c3c, #c0392b);
                    border-radius: 2px 2px 0 0;
                    animation: broken-spectrum-shake 2s ease-in-out infinite;
                    transform-origin: bottom center;
                    height: 60px;
                }
                
                .error-flash {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(231, 76, 60, 0.2);
                    animation: error-flash 3s ease-in-out infinite;
                }
                
                .error-icon {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 2.2rem;
                    animation: pulse-grow 2s ease-in-out infinite;
                }
                
                .blink-text {
                    animation: blink-text 1.5s ease-in-out infinite;
                }
                
                @keyframes broken-spectrum-shake {
                    0%, 100% { transform: rotate(-5deg); height: 40px; }
                    50% { transform: rotate(5deg); height: 60px; }
                }
                
                @keyframes error-flash {
                    0%, 100% { opacity: 0; }
                    50% { opacity: 0.3; }
                }
                
                @keyframes pulse-grow {
                    0%, 100% { transform: translate(-50%, -50%) scale(1); }
                    50% { transform: translate(-50%, -50%) scale(1.2); }
                }
                
                @keyframes blink-text {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.3; }
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