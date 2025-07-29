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
        self._dataset_type = None                # Type of loaded dataset (e.g., 'dm3', 'dm4')

        # Shared configuration and constants
        self._constants = Constants()
        self._colors = Colors()
        self._file_dropper = FileDropper()
        self._placeholders = Placeholders()
    
    @property
    def dataset(self) -> xr.Dataset | None:
        return self._dataset
    
    @property
    def dataset_type(self) -> str | None:
        return self._dataset_type

    def set_dataset(self, dataset: xr.Dataset, dataset_type: str = None):
        self._dataset = dataset
        self._dataset_type = dataset_type

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
    