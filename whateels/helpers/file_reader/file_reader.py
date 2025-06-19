import logging, os

from ...helpers.file_reader.abstract_classes import IDM_Parser, IDM_EELS_DataHandler, IFileReader
from ..parsers.dm34 import DM_InfoParser, DM_EELS_data

####################################################
# Setting up the logging system for this module
_log_fname = "dmReader.log"
_logger = logging.getLogger(__name__)
# _logger.setLevel(logging.INFO)
_logger.setLevel(logging.ERROR)
# These formatter keywords are not fstrings, but they work better
# with the logging module
_formatter = logging.Formatter(
    "%(asctime)s : %(name)s : \
    %(levelname)s : %(funcName)s : %(message)s"
)
_fhandler = logging.FileHandler(_log_fname)
_fhandler.setFormatter(_formatter)
_logger.addHandler(_fhandler)
#####################################################


# class DM_Reader(IFileReader):
class DM_EELS_Reader(IFileReader):
    """This class is the actual reader class that can be injected into whatEELS
    (or be used in a factory pattern scheme later ...)

    Dependencies
    --------------
    It will use the parser to get the information required to read the file later
    """

    def __init__(
        self,
        fname=None,
        parser: IDM_Parser = DM_InfoParser(),
        handler: IDM_EELS_DataHandler = DM_EELS_data(),
    ):
        """
        Reader initializer. Will check that a file name is given (fname),
        and that the actual name is a valid option for the reader.

        Parameters
        ----------------
        fname : str  =  Name of the file. If not provided, or empty string, an exception
                        is raised. If an incorrect file name is provided, or the route
                        to file cannot be found, an exception is raised. If the file
                        does not have the correct extension (dm3 or dm4), an exception
                        is raised. Default = None

        parser : IDM_Parser = Class of DM parser. Deafult = dm34_parsers.DM_InfoParser
                                The parser class can be modified. The only requirement to work
                                with this reader is that it provides a correct
        """
        # Checking if a file was actually provided
        if not fname:
            msg = "No file name provided."
            _logger.error(msg)
            raise NameError(msg)

        # Checking if we have a file or not
        if not os.path.isfile(fname):
            msg = f"The file-name given is not an actual file - {fname}."
            _logger.error(msg)
            raise NameError(msg)

        # At this point, the file should be loaded into the class
        self.fname = fname
        # We've given valid instances of the parsers and handlers
        self.parser = parser
        self.handler = handler

    def read_data(self):
        """
        This method will be in charge of reading the data. To do so,
        it parses (self.parser) first the entire file (self.fname), and then
        calls the data handler (self.handler).
        """
        _logger.info(f"Opening file {self.fname}")
        with open(self.fname, "rb") as f:
            _logger.info(
                f"Initialized parsing of file {self.fname}\n\
                Using {self.parser.__module__}"
            )
            # fparser = self.parser(f)
            self.parser.get_file(f)
            infoDict = self.parser.parse_file()
            _logger.info(f"Finalized parsing\n##############")
            _logger.info(f"Initialized data extraction using {self.handler.__module__}")
            self.handler.get_file_data(f, infoDict)
            sData = self.handler.handle_EELS_data()
            _logger.info(f"Finalized data extraction\n##############")
        return sData
