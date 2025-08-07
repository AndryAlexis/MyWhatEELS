from abc import ABC, abstractmethod

class IDM_Parser(ABC):
    """
    Abstrac class for the DMParser -
    Just in case that in the future the parser is changed or extended
    """

    @abstractmethod
    def get_file(self, *args, **kwargs):
        """Method that get the file opened file"""
        pass

    @abstractmethod
    def parse_file(self):
        """Method that parses the entire file"""
        pass
    
class IDM_EELS_DataHandler(ABC):
    """
    Abstrac class for the DM_EELS_data_Parser -
    Just in case that in the future the parser is changed or extended.
    Meant to work toguether eith the IDM_Parser, but not required if
    a different file type (e.g., raw image) is expected.
    """

    @abstractmethod
    def get_file_data(self, *args, **kwargs):
        # Method to get the opened file and parsed data dict
        pass

    @abstractmethod
    def handle_EELS_data(self):
        """Method that gets the relevant EELS data from the parsed files
        and passes it along as a dictionary"""
        pass
    
class IFileReader(ABC):
    """
    Abstract class for the file readers in whatEELS
    """

    @abstractmethod
    def read_data(self):
        pass
