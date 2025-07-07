"""
EELS Data Processor for handling scientific data processing operations.

This processor handles all EELS data processing operations including:
- Data reshaping and coordinate generation
- NaN/inf value cleaning
- xarray Dataset manipulation
- Data validation and transformation
"""

import numpy as np
import xarray as xr

class EELSDataProcessor:
    """
    Processes and cleans EELS electron count data for xarray datasets.
    
    This processor handles EELS data of various dimensionalities (1D, 2D, 3D) and
    converts them to a standardized format compatible with xarray datasets. It also
    provides data cleaning utilities to handle NaN/inf values common in scientific data.
    
    Key Operations:
    - Reshapes data from DM file format to xarray format
    - Generates appropriate spatial coordinates
    - Cleans NaN/inf values from data and coordinates
    - Handles spectrum images, spectrum lines, and single spectra
    """
    
    def process_data_for_xarray(self, electron_count_data, energy_axis):
        """
        Process and reshape data for xarray dataset creation.
        
        This method handles EELS data of different dimensionalities and converts
        them to a standardized format compatible with xarray datasets.
        
        Args:
            electron_count_data: Raw electron count data (1D, 2D, or 3D numpy array)
            energy_axis: Energy axis data (1D numpy array)
            
        Returns:
            tuple: (processed_data, x_coordinates, y_coordinates) or None if error
        """
        # Route to appropriate processing method based on data dimensionality
        if len(electron_count_data.shape) == 3:
            return self._process_3d_data(electron_count_data)
        elif len(electron_count_data.shape) == 2:
            return self._process_2d_data(electron_count_data, energy_axis)
        elif len(electron_count_data.shape) == 1:
            return self._process_1d_data(electron_count_data)
        else:
            print(f"ERROR: Unsupported data dimensionality: {electron_count_data.shape}")
            return None
    
    def _process_3d_data(self, electron_count_data):
        """
        Process 3D data (spectrum image: y × x × energy).
        
        For spectrum images, we need to transpose from the typical DM file format
        (energy, y, x) to xarray format (y, x, energy).
        """
        # Transpose from (energy, y, x) to (y, x, energy) for xarray compatibility
        electron_count_data = electron_count_data.transpose((1, 2, 0))
        
        # Generate spatial coordinates for the spectrum image
        y_coordinates = np.arange(0, electron_count_data.shape[0], dtype=np.int32)  # Pixel rows
        x_coordinates = np.arange(0, electron_count_data.shape[1], dtype=np.int32)  # Pixel columns
        
        return electron_count_data, x_coordinates, y_coordinates
    
    def _process_2d_data(self, electron_count_data, energy_axis):
        """
        Process 2D data (spectrum line: position × energy).
        
        2D data can be oriented as either (energy, position) or (position, energy).
        We need to determine the correct orientation and reshape it for xarray.
        """
        # Determine data orientation by comparing dimensions with energy axis
        if electron_count_data.shape[0] == len(energy_axis):
            # Data is (energy, position) - transpose to (position, energy)
            electron_count_data = electron_count_data.transpose()
            
        # Create coordinates: single row (y=0), multiple columns (x=positions)
        y_coordinates = np.array([0], dtype=np.int32)  # Only one spatial row
        x_coordinates = np.arange(0, electron_count_data.shape[0], dtype=np.int32)  # Position along line
        
        # Reshape to standard xarray format: (y, x, energy)
        shape_dimensions = [1, electron_count_data.shape[0], electron_count_data.shape[1]]
        electron_count_data = electron_count_data.reshape(shape_dimensions)
        
        return electron_count_data, x_coordinates, y_coordinates
    
    def _process_1d_data(self, electron_count_data):
        """
        Process 1D data (single spectrum: energy only).
        
        Single spectra need to be reshaped to fit the standard xarray format
        with artificial spatial coordinates.
        """
        # Create artificial spatial coordinates (single point at origin)
        x_coordinates = np.array([0], dtype=np.int32)  # Single point in x
        y_coordinates = np.array([0], dtype=np.int32)  # Single point in y
        
        # Reshape from (energy,) to (y=1, x=1, energy) format
        shape_dimensions = [1, 1]
        shape_dimensions.extend(list(electron_count_data.shape))
        electron_count_data = electron_count_data.reshape(shape_dimensions)
        
        return electron_count_data, x_coordinates, y_coordinates
    
    def clean_dataset(self, dataset):
        """
        Clean dataset by replacing NaN/inf values with zeros.
        
        Scientific data often contains NaN or infinite values that can cause
        issues in visualization and analysis. This method sanitizes the data
        by replacing problematic values with zeros.
        """
        try:
            # Clean the main electron count data array
            electron_count = dataset.ElectronCount.values
            electron_count = np.nan_to_num(electron_count, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Clean all coordinate arrays to prevent axis issues
            x_coords = dataset.coords['x'].values
            y_coords = dataset.coords['y'].values
            eloss_coords = dataset.coords['Eloss'].values
            
            # Sanitize coordinate arrays
            x_coords = np.nan_to_num(x_coords, nan=0.0, posinf=0.0, neginf=0.0)
            y_coords = np.nan_to_num(y_coords, nan=0.0, posinf=0.0, neginf=0.0)
            eloss_coords = np.nan_to_num(eloss_coords, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Reconstruct dataset with cleaned data and coordinates
            cleaned_dataset = xr.Dataset(
                {'ElectronCount': (dataset.ElectronCount.dims, electron_count)},
                coords={'x': x_coords, 'y': y_coords, 'Eloss': eloss_coords}
            )
            
            # Preserve original metadata attributes
            cleaned_dataset.attrs = dataset.attrs.copy()
            
            return cleaned_dataset
        except Exception as e:
            print(f"Warning: Could not clean dataset: {e}")
            return dataset
