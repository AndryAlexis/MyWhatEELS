"""
File Service for handling DM3/DM4 file operations.

This service handles all file-related operations including:
- File validation and size checking
- Temporary file management  
- DM3/DM4 file reading and parsing
- Error handling for file operations
"""

import os, numpy as np, xarray as xr, traceback
from pathlib import Path
from whateels.helpers import TempFile, DM_EELS_Reader

class FileService:
    """Service class for handling file operations"""
    
    def __init__(self, model):
        self.model = model
    
    def process_upload(self, filename: str, file_content: bytes):
        """
        Process file upload from bytes content.
        
        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file
            
        Returns:
            xarray.Dataset or None: Processed dataset or None if error
        """
        print(f"Starting file upload process for: {filename}")
        print(f"File content size: {len(file_content)} bytes")
        
        # Get the correct file extension from the uploaded filename
        file_extension = Path(filename).suffix
        
        # Create temporary file that will be automatically cleaned up
        with TempFile(suffix=file_extension, prefix=self.model.Constants.TEMP_PREFIX) as temp_path:
            try:
                # Write the file content to a temporary file
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                print(f"Temporary file created: {temp_path}")
                
                # Load the DM3/DM4 file and convert to xarray dataset
                dataset = self.load_dm_file(temp_path)
                
                if dataset is not None:
                    print(f"Dataset loaded successfully. Shape: {dataset.ElectronCount.shape}")
                    return dataset
                else:
                    print(f'Error loading file: {filename}')
                    return None
                    
            except Exception as e:
                print(f"Error during file upload processing: {e}")
                traceback.print_exc()
                return None
    
    def load_dm_file(self, filepath):
        """Load DM3/DM4 file and convert to xarray dataset"""
        try:
            print(f"Loading DM file: {filepath}")
            
            # Check file size first
            if not self._validate_file_size(filepath):
                return None
            
            # Use the DM_EELS_Reader from the whatEELS library
            print("Initializing DM_EELS_Reader...")
            spectrum_image = DM_EELS_Reader(filepath).read_data()
            print("DM file read successfully")
            
            # Get data and energy axis
            electron_count_data = spectrum_image.data
            energy_axis = spectrum_image.energy_axis
            
            print(f"Original data shape: {electron_count_data.shape}")
            print(f"Energy axis shape: {energy_axis.shape}")
            print(f"Energy axis range: {energy_axis.min():.2f} to {energy_axis.max():.2f}")
            
            # Check for NaN/inf in raw data
            self._log_data_quality(electron_count_data, energy_axis)
            
            # Clean energy axis for NaN/inf values
            energy_axis = np.nan_to_num(energy_axis, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Clean electron count data
            electron_count_data = np.nan_to_num(electron_count_data, nan=0.0, posinf=0.0, neginf=0.0)
            
            print("Data cleaned successfully")
            
            # Add metadata and return
            dataset = self._create_dataset_from_data(electron_count_data, energy_axis, spectrum_image, filepath)
            return dataset
            
        except Exception as exception:
            return self._handle_file_error(exception)
    
    def _validate_file_size(self, filepath):
        """Validate file size for DM files"""
        file_size = os.path.getsize(filepath)
        print(f"File size: {file_size} bytes")
        
        if file_size < 1000:  # Less than 1KB is suspicious for DM files
            print(f"Error: File size ({file_size} bytes) is too small for a valid DM3/DM4 file. Expected at least 1KB.")
            return False
        return True
    
    def _log_data_quality(self, electron_count_data, energy_axis):
        """Log data quality information"""
        data_nan_count = np.isnan(electron_count_data).sum()
        data_inf_count = np.isinf(electron_count_data).sum()
        energy_nan_count = np.isnan(energy_axis).sum()
        energy_inf_count = np.isinf(energy_axis).sum()
        
        print(f"Raw data NaN count: {data_nan_count}, Inf count: {data_inf_count}")
        print(f"Energy axis NaN count: {energy_nan_count}, Inf count: {energy_inf_count}")
    
    def _create_dataset_from_data(self, electron_count_data, energy_axis, spectrum_image, filepath):
        """Create xarray dataset from processed data"""
        from .eels_data_processor import EELSDataProcessor
        
        data_service = EELSDataProcessor()
        
        # Process the data using DataService
        processed_data = data_service.process_data_for_xarray(electron_count_data, energy_axis)
        
        if processed_data is None:
            return None
        
        electron_count_data, x_coordinates, y_coordinates = processed_data
        
        # Create xarray dataset
        print(f"Creating xarray dataset...")
        print(f"Data shape: {electron_count_data.shape}")
        print(f"Coordinate lengths - Y: {len(y_coordinates)}, X: {len(x_coordinates)}, Eloss: {len(energy_axis)}")
        
        # Validate dimensions match
        if electron_count_data.shape != (len(y_coordinates), len(x_coordinates), len(energy_axis)):
            print(f"ERROR: Shape mismatch!")
            print(f"Expected: ({len(y_coordinates)}, {len(x_coordinates)}, {len(energy_axis)})")
            print(f"Actual: {electron_count_data.shape}")
            return None
        
        dataset = xr.Dataset(
            {'ElectronCount': (['y', 'x', 'Eloss'], electron_count_data)},
            coords={'y': y_coordinates, 'x': x_coordinates, 'Eloss': energy_axis}
        )
        
        print("Dataset created successfully")
        
        # Clean dataset for NaN/inf values
        dataset = data_service.clean_dataset(dataset)
        print("Dataset cleaned successfully")
        
        # Add metadata
        dataset.attrs['original_name'] = os.path.basename(filepath)
        dataset.attrs['beam_energy'] = getattr(spectrum_image, 'beam_energy', 0)
        dataset.attrs['collection_angle'] = getattr(spectrum_image, 'collection_angle', 0.0)
        dataset.attrs['convergence_angle'] = getattr(spectrum_image, 'convergence_angle', 0.0)
        
        return dataset
    
    def _handle_file_error(self, exception):
        """Handle file loading errors"""
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
