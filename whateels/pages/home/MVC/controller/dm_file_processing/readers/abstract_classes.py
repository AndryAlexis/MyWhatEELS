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
    
class IFileReader(ABC):
    """
    Abstract class for the file readers in whatEELS
    """

    @abstractmethod
    def read_data(self):
        pass
