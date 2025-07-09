"""
DM File Parsing Exceptions

Exceptions related to DM3/DM4 file format parsing, structure validation,
and low-level file reading operations.
"""

from .base import DMFileError


class DMStructDataTypeError(DMFileError):
    """Raised when struct descriptor integers are not of simple_data_type."""
    
    def __init__(self, struct_format=None):
        super().__init__("Invalid struct data type in DM file", struct_format)


class DMStringReadingError(DMFileError):
    """Raised when string decoding fails with all available encoders."""
    
    def __init__(self, raw_data=None):
        super().__init__("Failed to decode string data from DM file", raw_data)


class DMDelimiterCharacterError(DMFileError):
    """Raised when delimiter between blocks or tags is incorrectly formatted."""
    
    def __init__(self, delimiter=None):
        super().__init__("Invalid delimiter character in DM file structure", delimiter)


class DMVersionError(DMFileError):
    """Raised when DM file version is not supported."""
    
    def __init__(self, version=None):
        super().__init__("Unsupported DM file version", version)


class DMIdentifierError(DMFileError):
    """Raised when data type identifier is incorrect or unknown."""
    
    def __init__(self, identifier=None):
        super().__init__("Unknown data type identifier in DM file", identifier)
