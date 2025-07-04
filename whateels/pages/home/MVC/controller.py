import param, panel as pn, os, xarray as xr, numpy as np
from pathlib import Path
from whateels.helpers import TempFile, DM_EELS_Reader, VisualDisplay

from .model import Model
from .view import View

class Controller:
    """
    Controller class for the home page of the WhatEELS application.
    This class handles file upload events and interacts with the Model and View.
    It processes uploaded DM3/DM4 files, converts them to xarray datasets,
    and updates the visualization in the View.
    """
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
    
    def handle_file_uploaded(self, filename: str, file_content: bytes):
        """
        Handle file upload from the FileDropper component.
        
        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file
        """
        
        # Get the correct file extension from the uploaded filename
        file_extension = Path(filename).suffix
        
        # Create temp file with 1-minute delay before deletion (60 seconds)
        with TempFile(suffix=file_extension, prefix=Model.Constants.TEMP_PREFIX) as temp_path:
            # Write the file content to a temporary file
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Load the DM3/DM4 file and convert to xarray dataset
            dataset = self._load_dm_file(temp_path)

            if dataset is not None:
                # Create visualization using VisualDisplay
                visualization = VisualDisplay(dataset)
                visualization.create_panels()
                
                # Update the view with the new visualization
                self.view.update_visualization(visualization.struc)
                print(f'Successfully loaded and visualized: {filename}')
            else:
                # Reset to placeholder on error
                self.view.reset_visualization()
                print(f'Error loading file: {filename}')
        

    def handle_file_removed(self, filename: str):
        """Handle file removal from the FileDropper component.
        Args:
            filename: Name of the removed file
        """
        print('File removed', filename)
        # Reset visualization to placeholder when file is removed
        self.view.reset_visualization()
    
    def _load_dm_file(self, filepath):
        """Load DM3/DM4 file and convert to xarray dataset"""
        try:
            # Check file size first
            file_size = os.path.getsize(filepath)
            if file_size < 1000:  # Less than 1KB is suspicious for DM files
                raise ValueError(f"File size ({file_size} bytes) is too small for a valid DM3/DM4 file. Expected at least 1KB.")
            
            # Use the DM_EELS_Reader from the whatEELS library
            spectrum_image = DM_EELS_Reader(filepath).read_data()
            
            # Get data and energy axis
            electron_count_data = spectrum_image.data
            energy_axis = spectrum_image.energy_axis
            
            # Reshape data for xarray (ensure it's in y, x, Eloss format)
            if len(electron_count_data.shape) == 3:
                electron_count_data = electron_count_data.transpose((1, 2, 0))
                y_coordinates = np.arange(0, electron_count_data.shape[0])
                x_coordinates = np.arange(0, electron_count_data.shape[1])
            elif len(electron_count_data.shape) == 2:
                y_coordinates = np.arange(0, electron_count_data.shape[1])
                x_coordinates = np.zeros((1), dtype=np.int32)
                shape_dimensions = list(electron_count_data.shape)
                shape_dimensions.insert(1, 1)
                electron_count_data = electron_count_data.reshape(shape_dimensions)
            elif len(electron_count_data.shape) == 1:
                x_coordinates = np.zeros((1), dtype=np.int32)
                y_coordinates = np.zeros((1), dtype=np.int32)
                shape_dimensions = [1, 1]
                shape_dimensions.extend(list(electron_count_data.shape))
                electron_count_data = electron_count_data.reshape(shape_dimensions)
            else:
                return None
            
            # Create xarray dataset
            dataset = xr.Dataset(
                {'ElectronCount': (['y', 'x', 'Eloss'], electron_count_data)},
                coords={'y': y_coordinates, 'x': x_coordinates, 'Eloss': energy_axis}
            )
            
            # Add metadata
            dataset.attrs['original_name'] = os.path.basename(filepath)
            dataset.attrs['beam_energy'] = getattr(spectrum_image, 'beam_energy', 0)
            dataset.attrs['collection_angle'] = getattr(spectrum_image, 'collection_angle', 0.0)
            dataset.attrs['convergence_angle'] = getattr(spectrum_image, 'convergence_angle', 0.0)
            
            return dataset
            
        except Exception as exception:
            error_message = str(exception)
            if "Expected versions 3 or 4" in error_message:
                print(f"Error loading DM file - Invalid or corrupted DM3/DM4 file: {exception}")
                return None
            elif "File size" in error_message and "too small" in error_message:
                print(f"Error loading DM file - File too small: {exception}")
                return None
            else:
                print(f"Error loading DM file: {exception}")
                return None
        