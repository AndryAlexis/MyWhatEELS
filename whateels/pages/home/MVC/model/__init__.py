import xarray as xr

from .constants import Constants, Colors, FileDropper, Placeholders

class Model:
    """
    Main application model for the WhatEELS home page.
    Stores the loaded EELS dataset, metadata, and shared configuration/state.
    """
    def __init__(self):
        # State attributes
        self._dataset: xr.Dataset | None = None  # Loaded EELS dataset

        # Shared configuration and constants
        self._constants = Constants()
        self._colors = Colors()
        self._file_dropper = FileDropper()
        self._placeholders = Placeholders()
    
    @property
    def dataset(self) -> xr.Dataset | None:
        return self._dataset
    @property
    def constants(self) -> Constants:
        return self._constants
    @property
    def colors(self) -> Colors:
        return self._colors
    @property
    def file_dropper(self) -> FileDropper:
        return self._file_dropper
    @property
    def placeholders(self) -> Placeholders:
        return self._placeholders
    
    @dataset.setter
    def dataset(self, dataset: xr.Dataset | None):
        """Set the EELS dataset and update any dependent state."""
        self._dataset = dataset
    