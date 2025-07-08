"""
Single spectrum visualization composer.
"""

import panel as pn
import holoviews as hv
import numpy as np

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SingleSpectrumVisualizer:
    """Composes single spectrum visualizations from EELS data"""
    
    def __init__(self, model):
        self.model = model
        self._STRETCH_WIDTH = 'stretch_width'
        self._STRETCH_BOTH = 'stretch_both'
    
    def create_layout(self):
        """Create layout for single spectrum visualization"""
        # Create spectrum plot
        spectrum_data = self.model.dataset.ElectronCount.squeeze()
        
        # Clean spectrum data for any remaining NaN/inf values
        spectrum_data = spectrum_data.fillna(0.0)
        spectrum_data = spectrum_data.where(np.isfinite(spectrum_data), 0.0)
        
        spectrum = hv.Curve(
            spectrum_data,
            kdims=[self.model.Constants.ELOSS],
            vdims=[self.model.Constants.ELECTRON_COUNT]
        ).opts(
            width=800,
            height=400,
            color=self.model.Colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='EELS Spectrum'
        )
        
        # Convert to Panel
        spectrum_pane = pn.pane.HoloViews(spectrum, sizing_mode=self._STRETCH_WIDTH)
        
        return pn.Column(
            spectrum_pane,
            sizing_mode=self._STRETCH_BOTH
        )
