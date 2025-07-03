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