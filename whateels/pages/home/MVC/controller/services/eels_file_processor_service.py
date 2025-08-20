"""
EELS File Processor for DM3/DM4 file operations.

Handles file I/O, validation, and orchestrates the file-to-dataset pipeline.
Manages temporary files and delegates data processing to EELSDataProcessor.
"""

import os, numpy as np, xarray as xr, traceback
from pathlib import Path
from whateels.errors.dm.data import DMEmptyInfoDictionary, DMNonEelsError
from whateels.helpers import TempFile
from whateels.shared_state import AppState
from ..dm_file_processing import DM_EELS_Reader
from .eels_data_processor_service import EELSDataProcessorService

class EELSFileProcessorService:
    """
    Handles DM3/DM4 file I/O and orchestrates file-to-dataset processing.
    
    Manages file validation, temporary files, and coordinates with EELSDataProcessor
    for scientific data operations.
    """
    
    def __init__(self, model):
        self._model = model

    # -- Public Methods --

    def process_upload(self, filename: str, file_content: bytes) -> xr.Dataset:
        """Process uploaded file bytes into EELS dataset."""
        # Get the correct file extension from the uploaded filename
        file_extension = Path(filename).suffix
        
        # Create temporary file that will be automatically cleaned up
        with TempFile(suffix=file_extension, prefix=self._model.constants.TEMP_PREFIX) as temp_path:
            try:
                # Write the file content to a temporary file
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                # Load the DM3/DM4 file and convert to xarray dataset
                dataset: xr.Dataset | None = self._load_dm_file(temp_path)

                if dataset is not None:
                    return dataset
                else:
                    print(f'Error loading file: {filename}')
                    return None
                    
            except Exception as e:
                print(f"Error during file upload processing: {e}")
                traceback.print_exc()
                return None

    # -- Private Methods --
    
    def _load_dm_file(self, filepath) -> xr.Dataset | None:
        """Load DM3/DM4 file and convert to xarray dataset with metadata."""
        try:
            # Check file size first
            if not self._validate_file_size(filepath):
                return None

            # Read the file
            dm_eels_reader = DM_EELS_Reader(filepath)

            # Get file metadata
            file_metadata_dictionary = dm_eels_reader.file_metadata
            spectrum_image = dm_eels_reader.processed_eels_spectrum

            # Store metadata
            self._store_metadata(file_metadata_dictionary)

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
            dataset: xr.Dataset | None = self._create_dataset_from_data(electron_count_data, energy_axis, spectrum_image, filepath)
            return dataset

        except Exception as exception:
            return self._handle_file_error(exception)

    def _store_metadata(self, infoDict=None):
        """
        Store file handle and metadata from parsed info dictionary.
        """
        if not infoDict:
            message = f"Expected an information dictionary from parser. None provided : {infoDict =}"
            raise DMEmptyInfoDictionary(message)
        try:
            # Store metadata in AppState for application-wide access
            AppState().metadata = infoDict
        except Exception:
            message = f"Failed to store metadata in AppState.\n{infoDict.keys() if infoDict else 'None'}"
            raise DMNonEelsError(message)

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
    
    def _create_dataset_from_data(self, electron_count_data, energy_axis, spectrum_image, filepath) -> xr.Dataset | None:
        """Create xarray dataset from processed data"""
        eels_data_processor = EELSDataProcessorService(self._model)
        
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
            dataset.attrs['image_name'] = spectrum_image.spectralInfo.get('Name', '')
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
