import os
import panel as pn
import xarray as xr
import numpy as np

from whateels.helpers.file_reader import DM_EELS_Reader
from whateels.helpers.visual_display import VisualDisplay
pn.extension('bokeh', 'tabulator')

class DMFileViewer():
    """Simple DM3/DM4 file viewer using Panel FileDropper"""
    
    def __init__(self):
        super().__init__()
        
        # Create FileDropper widget
        self.file_dropper = pn.widgets.FileInput(
            multiple=False,
            height=100,
            width=400
        )
        self.file_dropper.param.watch(self._on_file_upload, 'value')
        
        # Status message
        self.status_message = pn.pane.Markdown(
            "### Drop a DM3 or DM4 file here to view it",
            width=400,
            margin=(10, 0)
        )
        
        # Placeholder for the visualization
        self.visualization_pane = pn.pane.HTML(
            "<div style='width:1000px; height:550px; background-color:lightgray; display:flex; align-items:center; justify-content:center;'><h3>No file loaded</h3></div>",
            width=1000, 
            height=550
        )
        
        # Container for the actual visualization
        self.visualization_container = pn.Column(
            self.visualization_pane,
            width=1000,
            height=550
        )
        
        # Create layout
        self.layout = self._create_layout()
        
    def _on_file_upload(self, event):
        """Handle file upload event"""
        if self.file_dropper.value is None:
            return
            
        try:
            # Update status
            self.status_message.object = "### Loading file..."
            
            # Save uploaded file temporarily
            file_content = self.file_dropper.value
            filename = self.file_dropper.filename
            temp_path = os.path.join(os.getcwd(), filename)
            
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Load the DM3/DM4 file
            dataset = self._load_dm_file(temp_path)
            
            if dataset is not None:
                # Create visualization
                visualization = VisualDisplay(dataset)
                visualization.create_panels()
                
                # Replace the visualization container content
                self.visualization_container.clear()
                self.visualization_container.append(visualization.struc)
                
                # Update status
                self.status_message.object = f"### Successfully loaded: {filename}"
                
            else:
                # Reset to placeholder on error
                self.visualization_container.clear()
                self.visualization_container.append(self.visualization_pane)
                self.status_message.object = "### Error: Could not load the file"
                
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as exception:
            # Reset to placeholder on error
            self.visualization_container.clear()
            self.visualization_container.append(self.visualization_pane)
            
            error_message = str(exception)
            if "Expected versions 3 or 4" in error_message:
                self.status_message.object = "### Error: Invalid or corrupted DM3/DM4 file. Please check the file format."
            elif "File size" in error_message and "too small" in error_message:
                # Safely get file size
                try:
                    file_size = os.path.getsize(temp_path) if 'temp_path' in locals() and os.path.exists(temp_path) else 0
                    self.status_message.object = f"### Error: File too small ({file_size} bytes). DM3/DM4 files should be much larger."
                except:
                    self.status_message.object = "### Error: File too small. DM3/DM4 files should be much larger."
            else:
                self.status_message.object = f"### Error loading file: {str(exception)}"
            print(f"Error: {exception}")
            
            # Clean up temporary file if it exists
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
    
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
                # For spectrum images: (Eloss, Y, X) -> (Y, X, Eloss)
                electron_count_data = electron_count_data.transpose((1, 2, 0))
                dataset_type = 'SIm'
                y_coordinates = np.arange(0, electron_count_data.shape[0])
                x_coordinates = np.arange(0, electron_count_data.shape[1])
            elif len(electron_count_data.shape) == 2:
                # For spectrum lines: (Eloss, X) -> (X, 1, Eloss)
                dataset_type = 'SLi'
                y_coordinates = np.arange(0, electron_count_data.shape[1])
                x_coordinates = np.zeros((1), dtype=np.int32)
                shape_dimensions = list(electron_count_data.shape)
                shape_dimensions.insert(1, 1)
                electron_count_data = electron_count_data.reshape(shape_dimensions)
            elif len(electron_count_data.shape) == 1:
                # For single spectra: (Eloss,) -> (1, 1, Eloss)
                dataset_type = 'SSp'
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
    
    def _create_layout(self):
        """Create the Panel layout"""
        upload_section = pn.Column(
            pn.pane.Markdown("# DM3/DM4 File Viewer", width=400),
            self.status_message,
            self.file_dropper,
            width=400,
            margin=(20, 20)
        )
        
        main_layout = pn.Column(
            upload_section,
            pn.layout.Divider(),
            self.visualization_container,
            width=1200,
            height=800
        )
        
        return main_layout
    
    def show(self):
        """Show the application"""
        return self.layout.servable()

