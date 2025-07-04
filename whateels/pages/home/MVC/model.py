from pathlib import Path

class Model:
    """
    Model class for the home page of the WhatEELS application.
    This class contains constants and configurations used in the home page.
    """
    class Constants:
        # Get the base directory of the current file
        # This assumes the structure is: whateels/pages/home/MVC/model.py
        CSS_PATH = Path(__file__).parent.parent.parent / "assets" / "css" / "home.css"
        TITLE = "WhatEELS"
        TEMP_PREFIX = "whateels_"

    class FileDropper:
        TITLE = "Upload EELS data file"
        VALID_EXTENSIONS = ('.dm3', '.dm4')
        REJECT_MESSAGE = "❌ File rejected - only EELS data files (.dm3/.dm4) are supported"
        SUCCESS_MESSAGE = "✅ Ready to analyze your EELS data"
        FEEDBACK_MESSAGE = "No file uploaded yet... :("

    class Callbacks:
        FILE_UPLOADED = "handle_file_uploaded",
        FILE_REMOVED = "handle_file_removed"
    
    class Visualization:
        # Placeholder content for when no file is loaded
        PLACEHOLDER_HTML = """
        <div style='width:100%; height:550px; background-color:#f5f5f5; 
                    display:flex; align-items:center; justify-content:center;
                    border:2px dashed #ccc; border-radius:8px;'>
            <div style='text-align:center; color:#666;'>
                <h3>No file loaded</h3>
                <p>Upload a DM3 or DM4 file to see the visualization</p>
            </div>
        </div>
        """
        
        # Container dimensions
        CONTAINER_WIDTH = 1000
        CONTAINER_HEIGHT = 550