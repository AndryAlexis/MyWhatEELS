import os
import panel as pn
import xarray as xr
import numpy as np

from whateels.helpers.file_reader.file_reader import DM_EELS_Reader
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
            ds = self._load_dm_file(temp_path)
            
            if ds is not None:
                # Create visualization
                viz = VisualDisplay(ds)
                viz.create_panels()
                
                # Replace the visualization container content
                self.visualization_container.clear()
                self.visualization_container.append(viz.struc)
                
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
                
        except Exception as e:
            # Reset to placeholder on error
            self.visualization_container.clear()
            self.visualization_container.append(self.visualization_pane)
            
            error_msg = str(e)
            if "Expected versions 3 or 4" in error_msg:
                self.status_message.object = "### Error: Invalid or corrupted DM3/DM4 file. Please check the file format."
            elif "File size" in error_msg and "too small" in error_msg:
                # Safely get file size
                try:
                    file_size = os.path.getsize(temp_path) if 'temp_path' in locals() and os.path.exists(temp_path) else 0
                    self.status_message.object = f"### Error: File too small ({file_size} bytes). DM3/DM4 files should be much larger."
                except:
                    self.status_message.object = "### Error: File too small. DM3/DM4 files should be much larger."
            else:
                self.status_message.object = f"### Error loading file: {str(e)}"
            print(f"Error: {e}")
            
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
            si = DM_EELS_Reader(filepath).read_data()
            
            # Get data and energy axis
            data = si.data
            E = si.energy_axis
            
            # Reshape data for xarray (ensure it's in y, x, Eloss format)
            if len(data.shape) == 3:
                # For spectrum images: (Eloss, Y, X) -> (Y, X, Eloss)
                data = data.transpose((1, 2, 0))
                type_dataset = 'SIm'
                ys = np.arange(0, data.shape[0])
                xs = np.arange(0, data.shape[1])
            elif len(data.shape) == 2:
                # For spectrum lines: (Eloss, X) -> (X, 1, Eloss)
                type_dataset = 'SLi'
                ys = np.arange(0, data.shape[1])
                xs = np.zeros((1), dtype=np.int32)
                shap = list(data.shape)
                shap.insert(1, 1)
                data = data.reshape(shap)
            elif len(data.shape) == 1:
                # For single spectra: (Eloss,) -> (1, 1, Eloss)
                type_dataset = 'SSp'
                xs = np.zeros((1), dtype=np.int32)
                ys = np.zeros((1), dtype=np.int32)
                shap = [1, 1]
                shap.extend(list(data.shape))
                data = data.reshape(shap)
            else:
                return None
            
            # Create xarray dataset
            ds = xr.Dataset(
                {'ElectronCount': (['y', 'x', 'Eloss'], data)},
                coords={'y': ys, 'x': xs, 'Eloss': E}
            )
            
            # Add metadata
            ds.attrs['original_name'] = os.path.basename(filepath)
            ds.attrs['beam_energy'] = getattr(si, 'beam_energy', 0)
            ds.attrs['collection_angle'] = getattr(si, 'collection_angle', 0.0)
            ds.attrs['convergence_angle'] = getattr(si, 'convergence_angle', 0.0)
            
            return ds
            
        except Exception as e:
            error_msg = str(e)
            if "Expected versions 3 or 4" in error_msg:
                print(f"Error loading DM file - Invalid or corrupted DM3/DM4 file: {e}")
                return None
            elif "File size" in error_msg and "too small" in error_msg:
                print(f"Error loading DM file - File too small: {e}")
                return None
            else:
                print(f"Error loading DM file: {e}")
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

