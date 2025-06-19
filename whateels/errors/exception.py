# Exceptions for the DM reader
class DMStructDataTypeError(Exception):
    """
    Class defining a type of error in the reading structs in DM3/4 files
    If any of the descriptor integers in a struct is not of simple_data_type
    (check the types in the reader class), this error is raised
    """

    def __init__(self, value=None):
        self.dm3_struct_format = value

    def __str__(self):
        return repr(self.dm3_struct_format)


class DMStringReadingError(Exception):
    """
    Class defining a type of error in the reading strings in DM3/4 files
    If all the encoders put in the script fail to decript the string,
    this error is raised
    """

    def __init__(self, value=""):
        self.delimiter = value

    def __str__(self):
        return repr(self.delimiter)


class DMDelimiterCharacterError(Exception):
    """
    Class defining a type of error in the file structure read from DM3 or DM4 - If the delimiter
    between names of blocks or tags is formatted incorrectly
    """

    def __init__(self, value=""):
        self.delimiter = value

    def __str__(self):
        return repr(self.delimiter)


class DMVersionError(Exception):
    """
    Class defining a type of error in the DM info reader -
    Called uppon when the version of the file provided is
    not correct.
    """

    def __init__(self, value=None):
        self.dm3_version = value

    def __str__(self):
        return repr(self.dm3_version)


class DMIdentifierError(Exception):
    """
    Class defining a type of error in the DM info reader -
    Called uppon when the integer identifier for the type of
    data been read is incorrect
    """

    def __init__(self, value=None):
        self.identifier = value

    def __str__(self):
        return repr(self.identifier)


class DMNonEelsError(Exception):
    """
    Class defining a type of error in the DM EELS data handler
    It will be raised whenever the dictinary provided to to
    the information handler does not contain an actual spectral
    dataset.
    """

    def __init__(self, value=None):
        self.identifier = value

    def __str__(self):
        return repr(self.identifier)


class DMNonSupportedDataType(Exception):
    """
    Class defining a type of error in the DM EELS data handler
    It will be raised whenever the type specified in the parsed
    dictionary do not belong to a supported type to be read on NumPy
    """

    def __init__(self, value=None):
        self.identifier = value

    def __str__(self):
        return repr(self.identifier)


class DMConflictingDataTypeRead(Exception):
    """
    Class defining a type of error in the DM EELS data handler
    It will be raised whenever the type specified does not fit the
    number of items expected to be read and the size in bytes expected.
    """

    def __init__(self, value=None):
        self.identifier = value

    def __str__(self):
        return repr(self.identifier)


class DMEmptyInfoDictionary(Exception):
    """
    Class defining a type of error in the DM EELS data handler
    It will be raised whenever the dictinary is empty or not provided
    """

    def __init__(self, value=None):
        self.identifier = value

    def __str__(self):
        return repr(self.identifier)
