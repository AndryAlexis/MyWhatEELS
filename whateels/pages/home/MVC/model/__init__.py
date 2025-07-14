import xarray as xr

from .constants import Constants, Callbacks, Colors, FileDropper, Placeholders

class Model:
    """
    Model class for the home page of the WhatEELS application.
    This class contains constants and configurations used in the home page.
    """
    def __init__(self):
        #: The currently loaded EELS dataset (xarray.Dataset), or None if no file is loaded.
        #: This is set by the controller after a successful file upload and is used by all
        #: visualizer and interaction components to access EELS data and metadata.
        self.dataset: xr.Dataset | None = None
        self.dataset_type = None
        
        self._constants = Constants()
        self._callbacks = Callbacks()
        self._colors = Colors()
        self._file_dropper = FileDropper()
        self._placeholders = Placeholders()
    
    def set_dataset(self, dataset: xr.Dataset, dataset_type: str = None):
        """Set the dataset and its type"""
        self.dataset = dataset
        self.dataset_type = dataset_type
    
    @property
    def constants(self) -> Constants:
        """Get the constants used in the model"""
        return self._constants
    @property
    def callbacks(self) -> Callbacks:
        """Get the callback constants used in the model"""
        return self._callbacks
    @property
    def colors(self) -> Colors:
        """Get the color constants used in the model"""
        return self._colors
    @property
    def file_dropper(self) -> FileDropper:
        """Get the file dropper configuration"""
        return self._file_dropper
    @property
    def placeholders(self) -> Placeholders:
        """Get the placeholder text configuration"""
        return self._placeholders
    