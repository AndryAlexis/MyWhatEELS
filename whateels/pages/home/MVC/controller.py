import param, panel as pn, os, xarray as xr, numpy as np
import holoviews as hv
from pathlib import Path
from whateels.helpers import TempFile, DM_EELS_Reader

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
        
        # Add throttling for click events to prevent too frequent updates
        self._last_click_coords = (None, None)
        self._click_tolerance = 0.5  # Minimum distance to trigger update
        
        # Setup interaction callbacks
        self._setup_interactions()
    
    def _setup_interactions(self):
        """Setup interaction callbacks for visualization"""
        # This will be called after visualization is created
        # For now, we'll set up callbacks after the view creates the streams
        pass
    
    def setup_tap_callback(self, tap_stream):
        """Setup tap callback for interaction streams"""
        if tap_stream:
            tap_stream.add_subscriber(self._handle_tap_stream)
    
    def setup_hover_callback(self, hover_stream):
        """Setup hover callback for interaction streams - DEPRECATED"""
        # This method is kept for compatibility but we use tap now
        pass
    
    def _handle_hover_stream(self, **kwargs):
        """Handle hover events from HoloViews streams - DEPRECATED"""
        # This method is kept for compatibility but we use tap now
        pass
    
    def _handle_tap_stream(self, **kwargs):
        """Handle tap events from HoloViews streams"""
        # Extract x, y from stream parameters
        x = kwargs.get('x', None)
        y = kwargs.get('y', None)
        self._handle_tap_event(x, y)
    
    def _handle_tap_event(self, x, y):
        """Handle tap events on the visualization"""
        # Only update if coordinates are valid
        if x is None or y is None:
            return
            
        if self.model.dataset is None:
            return
        
        # Throttle click events - only update if position changed significantly
        last_x, last_y = self._last_click_coords
        if (last_x is not None and last_y is not None and 
            abs(x - last_x) < self._click_tolerance and abs(y - last_y) < self._click_tolerance):
            return
            
        # Update last click coordinates
        self._last_click_coords = (x, y)
            
        try:
            if self.model.dataset_type == self.model.Constants.SPECTRUM_IMAGE:
                # Get spectrum at clicked position
                spectrum = self.model.dataset.ElectronCount.sel(
                    x=x, y=y, method='nearest'
                )
                
                # Update the spectrum visualization
                self._update_spectrum_display(spectrum)
                
                # Update click feedback
                click_text = self.model.Constants.CLICK_TEXT_2D_TEMPLATE.format(int(x), int(y))
                if hasattr(self.view, 'click_feedback_widget') and self.view.click_feedback_widget:
                    self.view.click_feedback_widget.value = click_text
                
            elif self.model.dataset_type == self.model.Constants.SPECTRUM_LINE:
                # Get spectrum at clicked x position (y is not relevant for spectrum line)
                spectrum = self.model.dataset.ElectronCount.sel(
                    x=x, method='nearest'
                )
                
                # Update the spectrum visualization
                self._update_spectrum_display(spectrum)
                
                # Update click feedback
                click_text = self.model.Constants.CLICK_TEXT_1D_TEMPLATE.format(int(x))
                if hasattr(self.view, 'click_feedback_widget') and self.view.click_feedback_widget:
                    self.view.click_feedback_widget.value = click_text
                    
        except Exception as e:
            # Don't print errors for click events as they happen frequently
            pass
    
    def _update_spectrum_display(self, spectrum_data):
        """Update the spectrum display with new data"""
        try:
            # Check if the view and spectrum pane are still valid
            if not hasattr(self.view, 'spectrum_pane') or self.view.spectrum_pane is None:
                return
                
            # Check if the spectrum pane object is still alive (not removed)
            if not hasattr(self.view.spectrum_pane, 'object'):
                return
            
            # Create new spectrum curve
            spectrum_curve = hv.Curve(
                spectrum_data,
                kdims=[self.model.Constants.ELOSS],
                vdims=[self.model.Constants.ELECTRON_COUNT]
            ).opts(
                width=600,
                height=400,
                color=self.model.Colors.BLACK,
                line_width=2,
                xlabel='Energy Loss (eV)',
                ylabel='Electron Count',
                title='Selected Spectrum'
            )
            
            # Update the view's spectrum display safely
            try:
                self.view.spectrum_pane.object = spectrum_curve
            except Exception as update_error:
                # If update fails, the pane might have been removed - ignore silently
                pass
                
        except Exception as e:
            # Silently handle errors during hover updates
            pass
    
    def handle_file_uploaded(self, filename: str, file_content: bytes):
        """
        Handle file upload from the FileDropper component.
        
        Args:
            filename: Name of the uploaded file
            file_content: Binary content of the uploaded file
        """
        
        print(f"Starting file upload process for: {filename}")
        print(f"File content size: {len(file_content)} bytes")
        
        # Get the correct file extension from the uploaded filename
        file_extension = Path(filename).suffix
        
        # Create temp file with 1-minute delay before deletion (60 seconds)
        with TempFile(suffix=file_extension, prefix=Model.Constants.TEMP_PREFIX) as temp_path:
            try:
                # Write the file content to a temporary file
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                print(f"Temporary file created: {temp_path}")
                
                # Load the DM3/DM4 file and convert to xarray dataset
                dataset = self._load_dm_file(temp_path)

                if dataset is not None:
                    print(f"Dataset loaded successfully. Shape: {dataset.ElectronCount.shape}")
                    
                    # Reset click state for new file
                    self._last_click_coords = (None, None)
                    
                    # Set dataset in model
                    self.model.set_dataset(dataset)
                    
                    # Create visualization based on dataset type
                    visualization_component = self.view.create_eels_visualization(self.model.dataset_type)
                    
                    # Setup interaction callbacks - use tap instead of hover
                    if hasattr(self.view, 'tap_stream') and self.view.tap_stream:
                        self.setup_tap_callback(self.view.tap_stream)
                    
                    # Update the view with the new visualization
                    self.view.update_visualization(visualization_component)
                    print(f'Successfully loaded and visualized: {filename}')
                else:
                    # Reset to placeholder on error
                    self._last_click_coords = (None, None)
                    
                    self.view.reset_visualization()
                    print(f'Error loading file: {filename}')
                    
            except Exception as e:
                print(f"Error during file upload processing: {e}")
                import traceback
                traceback.print_exc()
                
                # Clean up click state on error
                self._last_click_coords = (None, None)
                
                self.view.reset_visualization()
        

    def handle_file_removed(self, filename: str):
        """Handle file removal from the FileDropper component.
        Args:
            filename: Name of the removed file
        """
        print('File removed', filename)
        
        # Reset click state
        self._last_click_coords = (None, None)
        
        # Reset visualization to placeholder when file is removed
        self.view.reset_visualization()
    
    def _load_dm_file(self, filepath):
        """Load DM3/DM4 file and convert to xarray dataset"""
        try:
            print(f"Loading DM file: {filepath}")
            
            # Check file size first
            file_size = os.path.getsize(filepath)
            print(f"File size: {file_size} bytes")
            
            if file_size < 1000:  # Less than 1KB is suspicious for DM files
                raise ValueError(f"File size ({file_size} bytes) is too small for a valid DM3/DM4 file. Expected at least 1KB.")
            
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
            data_nan_count = np.isnan(electron_count_data).sum()
            data_inf_count = np.isinf(electron_count_data).sum()
            energy_nan_count = np.isnan(energy_axis).sum()
            energy_inf_count = np.isinf(energy_axis).sum()
            
            print(f"Raw data NaN count: {data_nan_count}, Inf count: {data_inf_count}")
            print(f"Energy axis NaN count: {energy_nan_count}, Inf count: {energy_inf_count}")
            
            # Clean energy axis for NaN/inf values
            energy_axis = np.nan_to_num(energy_axis, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Clean electron count data
            electron_count_data = np.nan_to_num(electron_count_data, nan=0.0, posinf=0.0, neginf=0.0)
            
            print("Data cleaned successfully")
            
            # Reshape data for xarray (ensure it's in y, x, Eloss format)
            print(f"Reshaping data from shape: {electron_count_data.shape}")
            
            if len(electron_count_data.shape) == 3:
                electron_count_data = electron_count_data.transpose((1, 2, 0))
                y_coordinates = np.arange(0, electron_count_data.shape[0], dtype=np.int32)
                x_coordinates = np.arange(0, electron_count_data.shape[1], dtype=np.int32)
                print(f"3D data - Final shape: {electron_count_data.shape}")
                print(f"Coordinates - Y: {len(y_coordinates)}, X: {len(x_coordinates)}")
                
            elif len(electron_count_data.shape) == 2:
                # For 2D data, we need to be more careful about which dimension is which
                # Typically: (energy, position) or (position, energy)
                
                # Check if this is a spectrum line (energy vs position)
                if electron_count_data.shape[0] == len(energy_axis):
                    # Data is (energy, position) - transpose to (position, energy)
                    electron_count_data = electron_count_data.transpose()
                    
                y_coordinates = np.array([0], dtype=np.int32)  # Single y position
                x_coordinates = np.arange(0, electron_count_data.shape[0], dtype=np.int32)
                
                # Reshape to (y, x, energy) format
                shape_dimensions = [1, electron_count_data.shape[0], electron_count_data.shape[1]]
                electron_count_data = electron_count_data.reshape(shape_dimensions)
                
                print(f"2D data - Final shape: {electron_count_data.shape}")
                print(f"Coordinates - Y: {len(y_coordinates)}, X: {len(x_coordinates)}")
                print(f"Energy axis length: {len(energy_axis)}")
                print(f"Expected energy matches: {electron_count_data.shape[2] == len(energy_axis)}")
                
            elif len(electron_count_data.shape) == 1:
                x_coordinates = np.array([0], dtype=np.int32)
                y_coordinates = np.array([0], dtype=np.int32)
                shape_dimensions = [1, 1]
                shape_dimensions.extend(list(electron_count_data.shape))
                electron_count_data = electron_count_data.reshape(shape_dimensions)
                print(f"1D data - Final shape: {electron_count_data.shape}")
                print(f"Coordinates - Y: {len(y_coordinates)}, X: {len(x_coordinates)}")
                
            else:
                print(f"Unsupported data shape: {electron_count_data.shape}")
                return None
            
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
            dataset = self._clean_dataset(dataset)
            print("Dataset cleaned successfully")
            
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
    
    def _clean_dataset(self, dataset):
        """Clean dataset by replacing NaN/inf values with zeros"""
        try:
            # Replace NaN and infinite values with zeros in ElectronCount
            electron_count = dataset.ElectronCount.values
            electron_count = np.nan_to_num(electron_count, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Clean coordinates as well
            x_coords = dataset.coords['x'].values
            y_coords = dataset.coords['y'].values
            eloss_coords = dataset.coords['Eloss'].values
            
            # Clean coordinate arrays
            x_coords = np.nan_to_num(x_coords, nan=0.0, posinf=0.0, neginf=0.0)
            y_coords = np.nan_to_num(y_coords, nan=0.0, posinf=0.0, neginf=0.0)
            eloss_coords = np.nan_to_num(eloss_coords, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Create new dataset with cleaned data and coordinates
            cleaned_dataset = xr.Dataset(
                {'ElectronCount': (dataset.ElectronCount.dims, electron_count)},
                coords={'x': x_coords, 'y': y_coords, 'Eloss': eloss_coords}
            )
            
            # Copy attributes
            cleaned_dataset.attrs = dataset.attrs.copy()
            
            return cleaned_dataset
        except Exception as e:
            print(f"Warning: Could not clean dataset: {e}")
            return dataset
        