class Constants:
    TITLE = "WhatEELS"
    CSS_PATH = "whateels/assets/css/home.css"

class FILE_DROPPER:
    TITLE = "Upload EELS data file"
    VALID_EXTENSIONS = ('.dm3', '.dm4')
    REJECT_MESSAGE = "❌ File rejected - only EELS data files (.dm3/.dm4) are supported"
    SUCCESS_MESSAGE = "✅ Ready to analyze your EELS data"
    FEEDBACK_MESSAGE = "No file uploaded yet... :("

class CALLBACKS:
    FILE_UPLOAD = "handle_file_upload"

class Model:
    def __init__(self):
        pass