"""
DM Data Processing Exceptions

Exceptions related to EELS data validation, type checking,
and scientific data processing operations.
"""

from .base import DMFileError


class DMNonEelsError(DMFileError):
    """Raised when the DM file doesn't contain EELS spectral data."""
    
    def __init__(self, file_info=None):
        super().__init__("DM file does not contain EELS spectral data", file_info)


class DMNonSupportedDataType(DMFileError):
    """Raised when data type is not supported by NumPy."""
    
    def __init__(self, data_type=None):
        super().__init__("Data type not supported for NumPy operations", data_type)


class DMConflictingDataTypeRead(DMFileError):
    """Raised when data type doesn't match expected size or item count."""
    
    def __init__(self, conflict_info=None):
        super().__init__("Data type conflicts with expected size/count", conflict_info)


class DMEmptyInfoDictionary(DMFileError):
    """Raised when the info dictionary is empty or not provided."""
    
    def __init__(self, dict_info=None):
        super().__init__("Empty or missing info dictionary from DM file", dict_info)
