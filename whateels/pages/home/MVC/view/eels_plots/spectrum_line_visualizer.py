"""
Spectrum line visualization composer.
"""

import panel as pn
import holoviews as hv
import numpy as np
import xarray as xr

from holoviews import streams
from .abstract_eels_visualizer import AbstractEELSVisualizer
from typing import override

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SpectrumLineVisualizer(AbstractEELSVisualizer):
    """Composes spectrum line visualizations from EELS data"""
    
    # Text and label constants (specific to each plot)
    _IMAGE_X_LABEL = 'Position'
    _IMAGE_Y_LABEL = 'Energy Loss (eV)'
    _IMAGE_TITLE = 'EELS Spectrum Line'
    _SPECTRUM_X_LABEL = 'Energy Loss (eV)'
    _SPECTRUM_Y_LABEL = 'Electron Count'
    _SPECTRUM_TITLE = 'Selected Spectrum'
    _ERR_EMPTY_ELOSS = 'Energy loss coordinates are empty'

    # Constants for sizing modes and plot configuration
    _STRETCH_BOTH = 'stretch_both'
    _STRETCH_WIDTH = 'stretch_width'

    # Visualization configuration constants
    _MAX_PLOT_SIZE = 600
    _FOCUS_RATIO = 0.5
    _SPECTRUM_WIDTH = 600
    _SPECTRUM_HEIGHT = 300
    
    def __init__(self, model):
        print("Initializing DM4Plots")
        self.model = model
        self.tap_stream = None
        self.spectrum_pane = None
        # For tap/click throttling
        self._last_click_x = None
        self._click_tolerance = 0.5  # Minimum distance to trigger update

    @override
    def create_plots(self):
        """Create layout for spectrum line visualization with tap/click interaction."""
        # Sum over y dimension to create image
        image_data = self.model.dataset.ElectronCount.squeeze()
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        x_coords = self.model.dataset.coords[self.model.constants.AXIS_X]
        eloss_coords = self.model.dataset.coords[self.model.constants.ELOSS]
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        eloss_coords = eloss_coords.where(np.isfinite(eloss_coords), 0.0)
        clean_image_data = image_data.assign_coords({
            self.model.constants.AXIS_X: x_coords,
            self.model.constants.ELOSS: eloss_coords
        })
        image = self._create_image(clean_image_data, x_coords, eloss_coords)
        empty_spectrum = self._create_empty_spectrum(eloss_coords)
        # Setup tap interaction
        self.tap_stream = streams.Tap(x=0, y=0, source=image)
        self.tap_stream.add_subscriber(self._handle_tap_stream)
        image_pane = pn.pane.HoloViews(image, sizing_mode=self._STRETCH_BOTH)
        self.spectrum_pane = pn.pane.HoloViews(empty_spectrum, sizing_mode=self._STRETCH_BOTH)
        self._trigger_refresh(image_pane)
        return pn.Column(
            image_pane,
            self.spectrum_pane,
            sizing_mode=self._STRETCH_BOTH
        )

    def _handle_tap_stream(self, x=None, y=None, **kwargs):
        """Handle tap events from HoloViews streams for spectrum line."""
        # Only update if x is valid and changed significantly
        if x is None:
            return
        if self._last_click_x is not None and abs(x - self._last_click_x) < self._click_tolerance:
            return
        self._last_click_x = x
        self._update_spectrum_display(x)

    def _update_spectrum_display(self, x):
        """Update the spectrum pane with the spectrum at the tapped x position."""
        # Get spectrum at tapped x position
        try:
            spectrum = self.model.dataset.ElectronCount.sel(
                x=x, method='nearest'
            )
            # Ensure the spectrum is 1D by reducing over 'y' if present
            if 'y' in spectrum.dims:
                spectrum = spectrum.mean(dim='y')
        except Exception:
            return
        eloss_coords = self.model.dataset.coords[self.model.constants.ELOSS]
        spectrum_curve = hv.Curve(
            (eloss_coords, spectrum),
            kdims=[self.model.constants.ELOSS],
            vdims=[self.model.constants.ELECTRON_COUNT]
        ).opts(
            width=self._SPECTRUM_WIDTH,
            height=self._SPECTRUM_HEIGHT,
            color=self.model.colors.RED,
            line_width=2,
            xlabel=self._SPECTRUM_X_LABEL,
            ylabel=self._SPECTRUM_Y_LABEL,
            title=self._SPECTRUM_TITLE
        )
        if self.spectrum_pane is not None:
            self.spectrum_pane.object = spectrum_curve
    
    @override
    def create_dataset_info(self):
        attrs = self.model.dataset.attrs if self.model.dataset is not None else {}
        shape = attrs.get('shape', 'N/A')
        beam_energy = attrs.get('beam_energy', 'N/A')
        convergence_angle = attrs.get('convergence_angle', 'N/A')
        collection_angle = attrs.get('collection_angle', 'N/A')

        dataset_info = pn.Column(
            pn.pane.HTML("<h5 class='fdw-box-title'>Dataset Information</h5>", sizing_mode=self._STRETCH_WIDTH),
            pn.pane.Markdown(f"**Shape:** {shape}"),
            pn.pane.Markdown(f"**Beam Energy:** {beam_energy} keV"),
            pn.pane.Markdown(f"**Convergence Angle:** {convergence_angle} mrad"),
            pn.pane.Markdown(f"**Collection Angle:** {collection_angle} mrad"),
            sizing_mode=self._STRETCH_WIDTH
        )
        return dataset_info
    
    def _create_image(self, clean_image_data, x_coords, eloss_coords):
        """Create the spectrum line image"""
        # Calculate dimensions
        data_width = len(x_coords)
        data_height = len(eloss_coords)
        scale_factor = min(self._MAX_PLOT_SIZE / data_width, self._MAX_PLOT_SIZE / data_height)
        plot_width = int(data_width * scale_factor)
        plot_height = int(data_height * scale_factor)

        # Focus on energy range
        eloss_min, eloss_max = float(eloss_coords.min()), float(eloss_coords.max())
        eloss_range = eloss_max - eloss_min
        focused_range = eloss_range * self._FOCUS_RATIO
        eloss_center = (eloss_min + eloss_max) / 2
        focused_ylim = (eloss_center - focused_range/2, eloss_center + focused_range/2)

        return hv.Image(
            clean_image_data,
            kdims=[self.model.constants.AXIS_X, self.model.constants.ELOSS]
        ).opts(
            width=plot_width,
            height=plot_height,
            ylim=focused_ylim,
            cmap=self.model.colors.GREYS_R,
            xlabel=self._IMAGE_X_LABEL,
            ylabel=self._IMAGE_Y_LABEL,
            title=self._IMAGE_TITLE,
            invert_yaxis=True,
            tools=['hover', 'tap'],
            margin=0,
            padding=0,
        )
    
    def _create_empty_spectrum(self, eloss_coords):
        """Create empty spectrum for interaction"""
        empty_data = xr.zeros_like(eloss_coords)
        
        if len(eloss_coords) == 0:
            raise ValueError(self._ERR_EMPTY_ELOSS)
        
        return hv.Curve(
            (eloss_coords, empty_data),
            kdims=[self.model.constants.ELOSS],
            vdims=[self.model.constants.ELECTRON_COUNT]
        ).opts(
            width=self._SPECTRUM_WIDTH,
            height=self._SPECTRUM_HEIGHT,
            color=self.model.colors.BLACK,
            line_width=2,
            xlabel=self._SPECTRUM_X_LABEL,
            ylabel=self._SPECTRUM_Y_LABEL,
            title=self._SPECTRUM_TITLE
        )
    
    def _trigger_refresh(self, image_pane):
        """Programmatically trigger refresh for square display"""
        def trigger_refresh():
            image_pane.param.watchers.clear()
            image_pane._update_pane()
        
        pn.state.add_periodic_callback(trigger_refresh, period=0, count=1)
