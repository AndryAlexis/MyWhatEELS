"""
Base DM File Exception Classes

Foundation exception classes for Digital Micrograph (DM3/DM4) file operations.
"""


class DMFileError(Exception):
    """Base exception for all DM file reading errors."""
    
    def __init__(self, message: str, value=None):
        self.message = message
        self.value = value
        super().__init__(self.message)
    
    def __str__(self):
        if self.value is not None:
            return f"{self.message}: {self.value}"
        return self.message
