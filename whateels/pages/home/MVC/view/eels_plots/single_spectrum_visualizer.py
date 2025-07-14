"""
Single spectrum visualization composer.
"""

import holoviews as hv
import numpy as np

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class SingleSpectrumVisualizer:
    """Composes single spectrum visualizations from EELS data"""
    
    # Constants for sizing modes
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'
    
    def __init__(self, model):
        print("Initializing SingleSpectrumVisualizer")
        self.model = model

    def get_clean_spectrum_data(self):
        """Return cleaned spectrum data for plotting (no plotting here)"""
        spectrum_data = self.model.dataset.ElectronCount.squeeze()
        spectrum_data = spectrum_data.fillna(0.0)
        spectrum_data = spectrum_data.where(np.isfinite(spectrum_data), 0.0)
        return spectrum_data
