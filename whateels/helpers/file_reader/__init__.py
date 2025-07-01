"""
File Reader Module for DM3/DM4 EELS Data

This module provides functionality to read and process EELS (Electron Energy Loss Spectroscopy) 
data from Gatan DigitalMicrograph files (DM3/DM4 format).

The main class DM_EELS_Reader follows a two-stage process:
1. Parse file structure and metadata using a DM parser
2. Extract and handle EELS data using a specialized data handler

Classes
-------
DM_EELS_Reader : Main reader class for DM3/DM4 files containing EELS data
"""

import logging
import os

from .abstract_classes import IDM_Parser, IDM_EELS_DataHandler, IFileReader
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
    """
    Reader class for DM3/DM4 files containing EELS (Electron Energy Loss Spectroscopy) data.
    
    This class can be injected into whatEELS or used in a factory pattern scheme.
    It uses a parser to extract file information and a handler to process the EELS data.
    
    Dependencies
    ------------
    - parser: Extracts structural information from DM files
    - handler: Processes and converts EELS data to usable format
    """

    def __init__(
        self,
        filename=None,
        parser: IDM_Parser = DM_InfoParser(),
        handler: IDM_EELS_DataHandler = DM_EELS_data(),
    ):
        """
        Initialize the DM EELS reader.

        Parameters
        ----------
        filename : str, optional
            Path to the DM3/DM4 file to read. Must be a valid file path.
            Raises NameError if not provided or if file doesn't exist.
            Default is None.
            
        parser : IDM_Parser, optional
            DM file parser instance. Must implement IDM_Parser interface.
            Default is DM_InfoParser().
            
        handler : IDM_EELS_DataHandler, optional  
            EELS data handler instance. Must implement IDM_EELS_DataHandler interface.
            Default is DM_EELS_data().
            
        Raises
        ------
        NameError
            If filename is not provided, file doesn't exist, or has wrong extension.
        """
        # Validate that a filename was provided
        if not filename:
            error_message = "No file name provided."
            _logger.error(error_message)
            raise NameError(error_message)

        # Validate that the file exists
        if not os.path.isfile(filename):
            error_message = f"The file-name given is not an actual file - {filename}."
            _logger.error(error_message)
            raise NameError(error_message)

        # Store validated components
        self.filename = filename
        self.parser = parser
        self.handler = handler

    def read_data(self):
        """
        Read and process EELS data from the DM file.
        
        This method performs a two-step process:
        1. Parse the file structure to extract metadata and data organization
        2. Handle the EELS data extraction and conversion
        
        Returns
        -------
        object
            Processed EELS data object containing the spectroscopy data and metadata
            
        Raises
        ------
        Various exceptions may be raised during file parsing or data handling
        """
        _logger.info(f"Opening file {self.filename}")
        
        with open(self.filename, "rb") as binary_file_stream:
            # Step 1: Parse file structure and extract metadata
            _logger.info(f"Starting file parsing for {self.filename}")
            _logger.info(f"Using parser: {self.parser.__module__}")
            
            self.parser.get_file(binary_file_stream)
            file_metadata_dictionary = self.parser.parse_file()
            
            _logger.info("File parsing completed successfully")
            _logger.info("##############")
            
            # Step 2: Extract and process EELS data
            _logger.info(f"Starting EELS data extraction using: {self.handler.__module__}")
            
            self.handler.get_file_data(binary_file_stream, file_metadata_dictionary)
            processed_eels_spectrum = self.handler.handle_EELS_data()
            
            _logger.info("EELS data extraction completed successfully")
            _logger.info("##############")
            
        return processed_eels_spectrum
