"""
EELS File Processor for DM3/DM4 file operations.

Handles file I/O, validation, and orchestrates the file-to-dataset pipeline.
Manages temporary files and delegates data processing to EELSDataProcessor.
"""

import os, numpy as np, xarray as xr, traceback
from pathlib import Path
from whateels.helpers import TempFile
from ..dm_file_processing import DM_EELS_Reader
from .eels_data_processor import EELSDataProcessor

class EELSFileProcessor:
    """
    Handles DM3/DM4 file I/O and orchestrates file-to-dataset processing.
    
    Manages file validation, temporary files, and coordinates with EELSDataProcessor
    for scientific data operations.
    """
    
    def __init__(self, model):
        self.model = model
    
    def process_upload(self, filename: str, file_content: bytes) -> xr.Dataset:
        """Process uploaded file bytes into EELS dataset."""
        # Get the correct file extension from the uploaded filename
        file_extension = Path(filename).suffix
        
        # Create temporary file that will be automatically cleaned up
        with TempFile(suffix=file_extension, prefix=self.model.constants.TEMP_PREFIX) as temp_path:
            try:
                # Write the file content to a temporary file
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                # Load the DM3/DM4 file and convert to xarray dataset
                dataset = self.load_dm_file(temp_path)
                
                if dataset is not None:
                    return dataset
                else:
                    print(f'Error loading file: {filename}')
                    return None
                    
            except Exception as e:
                print(f"Error during file upload processing: {e}")
                traceback.print_exc()
                return None
            
    def extract_all_spectrum_image_attributes(self, spectrum_image):
        dictionary = {}
        for attr in dir(spectrum_image):
            # Skip private/protected and methods
            if attr.startswith("_"):
                continue
            try:
                value = getattr(spectrum_image, attr)
                # Skip methods
                if callable(value):
                    continue
                dictionary[attr] = value
            except Exception as e:
                print(f"{attr}: <error reading attribute: {e}>")
        return dictionary
    
    def _become_json_format(self, dictionary):
        """Convert dictionary to JSON format, handling numpy arrays and non-serializable objects."""
        import json
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.generic,)):
                return obj.item()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [convert(i) for i in obj]
            # Handle non-serializable objects (e.g., file handles)
            try:
                json.dumps(obj)
            except (TypeError, OverflowError):
                return f"<{type(obj).__name__} object>"
            return obj
        return json.dumps(convert(dictionary), indent=4, sort_keys=True)
    
    def _generate_json_file(self, filename, json_representation):
        """Generate a JSON file from the given JSON representation in the project root."""
        json_filename = f"{Path(filename).stem}.json"
        # Find the project root (assume it's two levels up from this file)
        project_root = Path(__file__).resolve().parents[6]
        json_filepath = project_root / json_filename

        with open(json_filepath, 'w') as json_file:
            json_file.write(json_representation)

    def load_dm_file(self, filepath):
        """Load DM3/DM4 file and convert to xarray dataset with metadata."""
        try:
            # Check file size first
            if not self._validate_file_size(filepath):
                return None

            # Use the DM_EELS_Reader from the whatEELS library
            spectrum_image = DM_EELS_Reader(filepath).read_data()

            # Get data and energy axis
            electron_count_data = spectrum_image.data
            energy_axis = spectrum_image.energy_axis

            # Check for NaN/inf in raw data
            self._log_data_quality(electron_count_data, energy_axis)

            # Clean energy axis for NaN/inf values
            energy_axis = np.nan_to_num(energy_axis, nan=0.0, posinf=0.0, neginf=0.0)

            # Clean electron count data
            electron_count_data = np.nan_to_num(electron_count_data, nan=0.0, posinf=0.0, neginf=0.0)

            # Add metadata and return
            dataset = self._create_dataset_from_data(electron_count_data, energy_axis, spectrum_image, filepath)
            return dataset

        except Exception as exception:
            return self._handle_file_error(exception)
    
    def _validate_file_size(self, filepath):
        """Validate file size for DM files"""
        file_size = os.path.getsize(filepath)
        
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
        
        # Only log if there are quality issues
        if data_nan_count > 0 or data_inf_count > 0:
            print(f"Warning: Raw data has {data_nan_count} NaN values and {data_inf_count} Inf values")
        if energy_nan_count > 0 or energy_inf_count > 0:
            print(f"Warning: Energy axis has {energy_nan_count} NaN values and {energy_inf_count} Inf values")
    
    def _create_dataset_from_data(self, electron_count_data, energy_axis, spectrum_image, filepath):
        """Create xarray dataset from processed data"""
        eels_data_processor = EELSDataProcessor(self.model)
        
        # Process the data using DataService
        processed_data = eels_data_processor.process_data_for_xarray(electron_count_data, energy_axis)
        
        if processed_data is None:
            return None
        
        electron_count_data, x_coordinates, y_coordinates = processed_data
        
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
        
        # Clean dataset for NaN/inf values
        dataset = eels_data_processor.clean_dataset(dataset)
        
        # Determine dataset type using the data service
        dataset_type = eels_data_processor.determine_dataset_type(dataset)
        
        # Add metadata
        dataset.attrs['original_name'] = os.path.basename(filepath)
        dataset.attrs['dataset_type'] = dataset_type
        dataset.attrs['beam_energy'] = getattr(spectrum_image, 'beam_energy', 0)
        dataset.attrs['collection_angle'] = getattr(spectrum_image, 'collection_angle', 0.0)
        dataset.attrs['convergence_angle'] = getattr(spectrum_image, 'convergence_angle', 0.0)

        try:
            image_name = spectrum_image.spectralInfo.get('Name', '')
        except Exception:
            image_name = ''
        dataset.attrs['image_name'] = image_name

        try:
            dataset.attrs['shape'] = list(dataset['ElectronCount'].shape)
        except Exception:
            pass
        
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
