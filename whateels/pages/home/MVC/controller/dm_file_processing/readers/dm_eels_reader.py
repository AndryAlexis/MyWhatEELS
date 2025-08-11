"""
DM3/DM4 EELS Data Reader

Reads EELS data from Gatan DigitalMicrograph files using a two-stage process:
1. Parse file structure and metadata
2. Extract and process EELS spectroscopic data

Supports dependency injection for custom parsers and handlers.

Example
-------
    reader = DM_EELS_Reader("spectrum.dm4")
    eels_data = reader.read_data()
"""

import os

from typing import TYPE_CHECKING
from .abstract_classes import IFileReader
from ..parsers import DM_InfoParser, DM_EELS_data
from whateels.helpers.logging import Logger

if TYPE_CHECKING:
    from .abstract_classes import IDM_Parser

_logger = Logger.get_logger("dm_file_reader.log", __name__)

class DM_EELS_Reader(IFileReader):
    """
    Reader for DM3/DM4 files containing EELS data.
    
    Uses dependency injection pattern with separate parser and handler components.
    Processes data through a two-stage pipeline: file parsing then EELS data extraction.
    
    Parameters
    ----------
    filename : str
        Path to DM3/DM4 file
    parser : IDM_Parser, optional
        File parser (defaults to DM_InfoParser)
    handler : DM_EELS_data, optional
        Data handler (defaults to DM_EELS_data)
    """

    def __init__(
        self,
        filename: str,
        parser: "IDM_Parser" = None,
        handler: "DM_EELS_data" = None,
    ):
        """
        Initialize reader with file validation and component injection.

        Parameters
        ----------
        filename : str
            Path to DM3/DM4 file to read
        parser : IDM_Parser, optional
            Custom parser (default: DM_InfoParser)
        handler : DM_EELS_data, optional  
            Custom handler (default: DM_EELS_data)
        """
        self.filename = filename
        self.parser = parser or DM_InfoParser()
        self.handler = handler or DM_EELS_data()

    def read_data(self):
        """
        Read and process EELS data from the DM file.
        
        Performs two-stage processing: file parsing then EELS data extraction.
        
        Returns
        -------
        object
            Processed EELS data with spectroscopy information and metadata
            
        Raises
        ------
        Exception
            Various exceptions during file parsing or data handling
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
