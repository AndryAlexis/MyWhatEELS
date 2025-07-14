class FileDropper:
    TITLE = "Upload EELS data file"
    VALID_EXTENSIONS = ('.dm3', '.dm4')
    REJECT_MESSAGE = "❌ File rejected - only EELS data files (.dm3/.dm4) are supported"
    SUCCESS_MESSAGE = "✅ Ready to analyze your EELS data"
    FEEDBACK_MESSAGE = "No file uploaded yet... :("