"""
Spectrum image (datacube) visualization composer.
"""

import panel as pn
import holoviews as hv
from holoviews import streams
import numpy as np
import xarray as xr

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SpectrumImageVisualizer:
    """Composes spectrum image (datacube) visualizations from EELS data"""
    
    def __init__(self, model):
        self.model = model
        self._STRETCH_WIDTH = 'stretch_width'
        self._STRETCH_BOTH = 'stretch_both'
        self.tap_stream = None
        self.spectrum_pane = None
    
    def create_layout(self):
        """Create layout for spectrum image (datacube) visualization"""
        # Create reference image (sum over energy loss)
        image_data = self.model.dataset.ElectronCount.sum(self.model.Constants.ELOSS)
        
        # Clean image data
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        
        # Clean coordinates
        x_coords = self.model.dataset.coords[self.model.Constants.AXIS_X]
        y_coords = self.model.dataset.coords[self.model.Constants.AXIS_Y]
        
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        y_coords = y_coords.where(np.isfinite(y_coords), 0.0)
        
        # Create clean dataset
        clean_image_data = image_data.assign_coords({
            self.model.Constants.AXIS_X: x_coords,
            self.model.Constants.AXIS_Y: y_coords
        })
        
        # Create components
        image = self._create_image(clean_image_data, x_coords, y_coords)
        empty_spectrum = self._create_empty_spectrum()
        
        # Setup interaction
        self.tap_stream = streams.Tap(x=0, y=0, source=image)
        
        # Convert to Panel
        image_pane = pn.pane.HoloViews(image, sizing_mode=self._STRETCH_WIDTH)
        self.spectrum_pane = pn.pane.HoloViews(empty_spectrum, sizing_mode=self._STRETCH_WIDTH)
        
        return pn.Row(
            pn.Column(
                image_pane,
                sizing_mode=self._STRETCH_WIDTH
            ),
            self.spectrum_pane,
            sizing_mode=self._STRETCH_BOTH
        )
    
    def _create_image(self, clean_image_data, x_coords, y_coords):
        """Create the spectrum image"""
        # Calculate data aspect ratio for square pixels
        x_step = float(x_coords[1] - x_coords[0]) if len(x_coords) > 1 else 1.0
        y_step = float(y_coords[1] - y_coords[0]) if len(y_coords) > 1 else 1.0
        pixel_aspect = x_step / y_step if y_step != 0 else 1.0
        
        return hv.Image(
            clean_image_data,
            kdims=[self.model.Constants.AXIS_X, self.model.Constants.AXIS_Y]
        ).opts(
            width=500,
            height=500,
            cmap=self.model.Colors.GREYS_R,
            xlabel='X Position',
            ylabel='Y Position',
            title='EELS Image (Sum over Energy)',
            invert_yaxis=True,
            tools=['hover', 'tap'],
            data_aspect=pixel_aspect,
            margin=0,
            padding=0.02
        )
    
    def _create_empty_spectrum(self):
        """Create empty spectrum for interaction"""
        eloss_coords = self.model.dataset.coords[self.model.Constants.ELOSS]
        empty_data = xr.zeros_like(eloss_coords)
        
        if len(eloss_coords) == 0:
            raise ValueError("Energy loss coordinates are empty")
        
        return hv.Curve(
            (eloss_coords, empty_data),
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
