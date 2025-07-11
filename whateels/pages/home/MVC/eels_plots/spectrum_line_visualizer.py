"""
Spectrum line visualization composer.
"""

import panel as pn
import holoviews as hv
from holoviews import streams
import numpy as np
import xarray as xr

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SpectrumLineVisualizer:
    """Composes spectrum line visualizations from EELS data"""
    
    def __init__(self, model):
        self.model = model
        self._STRETCH_WIDTH = 'stretch_width'
        self._STRETCH_BOTH = 'stretch_both'
        self.tap_stream = None
        self.spectrum_pane = None
    
    def create_layout(self):
        """Create layout for spectrum line visualization"""
        # Sum over y dimension to create image
        image_data = self.model.dataset.ElectronCount.squeeze()
        
        # Clean image data for any remaining NaN/inf values
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        
        # Clean coordinates
        x_coords = self.model.dataset.coords[self.model.Constants.AXIS_X]
        eloss_coords = self.model.dataset.coords[self.model.Constants.ELOSS]
        
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        eloss_coords = eloss_coords.where(np.isfinite(eloss_coords), 0.0)
        
        # Create clean dataset for the image
        clean_image_data = image_data.assign_coords({
            self.model.Constants.AXIS_X: x_coords,
            self.model.Constants.ELOSS: eloss_coords
        })
        
        # Create image and spectrum components
        image = self._create_image(clean_image_data, x_coords, eloss_coords)
        empty_spectrum = self._create_empty_spectrum(eloss_coords)
        
        # Setup interaction
        self.tap_stream = streams.Tap(x=0, y=0, source=image)
        
        # Convert to Panel
        image_pane = pn.pane.HoloViews(image, sizing_mode=self._STRETCH_BOTH)
        self.spectrum_pane = pn.pane.HoloViews(empty_spectrum, sizing_mode=self._STRETCH_BOTH)
        
        # Trigger refresh for square display
        self._trigger_refresh(image_pane)
        
        return pn.Column(
            image_pane,
            self.spectrum_pane,
            sizing_mode=self._STRETCH_BOTH
        )
    
    def _create_image(self, clean_image_data, x_coords, eloss_coords):
        """Create the spectrum line image"""
        # Calculate dimensions
        data_width = len(x_coords)
        data_height = len(eloss_coords)
        
        scale_factor = min(600 / data_width, 600 / data_height)
        plot_width = int(data_width * scale_factor)
        plot_height = int(data_height * scale_factor)
        
        # Focus on energy range
        eloss_min, eloss_max = float(eloss_coords.min()), float(eloss_coords.max())
        eloss_range = eloss_max - eloss_min
        focus_ratio = 0.5
        focused_range = eloss_range * focus_ratio
        eloss_center = (eloss_min + eloss_max) / 2
        focused_ylim = (eloss_center - focused_range/2, eloss_center + focused_range/2)
        
        return hv.Image(
            clean_image_data,
            kdims=[self.model.Constants.AXIS_X, self.model.Constants.ELOSS]
        ).opts(
            width=plot_width,
            height=plot_height,
            ylim=focused_ylim,
            cmap=self.model.Colors.GREYS_R,
            xlabel='Position',
            ylabel='Energy Loss (eV)',
            title='EELS Spectrum Line',
            invert_yaxis=True,
            tools=['hover', 'tap'],
            margin=0,
            padding=0,
        )
    
    def _create_empty_spectrum(self, eloss_coords):
        """Create empty spectrum for interaction"""
        empty_data = xr.zeros_like(eloss_coords)
        
        if len(eloss_coords) == 0:
            raise ValueError("Energy loss coordinates are empty")
        
        return hv.Curve(
            (eloss_coords, empty_data),
            kdims=[self.model.Constants.ELOSS],
            vdims=[self.model.Constants.ELECTRON_COUNT]
        ).opts(
            width=600,
            height=300,
            color=self.model.Colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='Selected Spectrum'
        )
    
    def _trigger_refresh(self, image_pane):
        """Programmatically trigger refresh for square display"""
        def trigger_refresh():
            image_pane.param.watchers.clear()
            image_pane._update_pane()
        
        pn.state.add_periodic_callback(trigger_refresh, period=0, count=1)
