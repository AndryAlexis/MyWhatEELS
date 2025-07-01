"""
Model layer for EELS visualization - contains data models, constants, and state management.
"""

import xarray as xr
import numpy as np
from typing import Tuple, Optional


class Constants:
    """Centralized constants for EELS visualization."""
    
    # Axis names
    AXIS_X = 'x'
    AXIS_Y = 'y'
    ELOSS = 'Eloss'
    ELECTRON_COUNT = 'ElectronCount'
    CLICK_TEXT = 'click_text'

    # Dataset types
    SINGLE_SPECTRUM = 'SSp'
    SPECTRUM_LINE = 'SLi'
    SPECTRUM_IMAGE = 'SIm'
    
    # Component attribute names
    SPECTRUM_HOVER_ATTR = 'spectrum_hover'
    SPECTRUM_TAP_ATTR = 'spectrum_tap'

    # Click text templates
    CLICK_TEXT_1D_TEMPLATE = '|- y : {} -|'
    CLICK_TEXT_2D_TEMPLATE = '|- x : {} -|- y : {} -|'
    CLICK_TEXT_1D_NONE = '|- y : None -|'
    CLICK_TEXT_2D_NONE = '|- x : None -|- y : None -|'
    
    # None string
    NONE_TEXT = 'None'

class Colors:
    """Color constants for visualization styling."""
    
    GREYS_R = 'Greys_r'
    GREY = 'grey'
    BLACK = 'black'
    WHITE = 'white'
    RED = 'red'
    LIMEGREEN = 'limegreen'
    DARKGREY = 'darkgrey'
    GHOSTWHITE = 'ghostwhite'
    ORANGERED = 'orangered'
    DARKRED = 'darkred'
    MIDNIGHTBLUE = 'midnightblue'
    GAINSBORO = 'gainsboro'

class Formatters:
    """Formatting constants for data display."""
    
    # Bokeh/HoloViews formatters (printf-style)
    SCIENTIFIC = '%+.1e'
    INTEGER = '%.0f'
    
    # Python f-string formatters
    SCIENTIFIC_ELECTRON_COUNTS = ':+.1e'
    INTEGER_Y_SL = ':.0f'
    INTEGER_PADDED = ':>12.0f'  # Right-aligned with padding
    INTEGER_5D = ':5d'
    FLOAT_9_2F = ':9.2f'

class UIConfig:
    """UI configuration constants."""
    
    # Tools
    HOVER_TAP_TOOLS = ['hover', 'tap']
    
    # Dimensions lists
    KDIMS_XY = ['x', 'y']
    KDIMS_Y_ELOSS = ['y', 'Eloss']
    
    # Labels
    TICK_FORMATTERS_LABEL = 'Tick formatters'
    DATASET_DISPLAY_LABEL = 'DataSet on Display'
    SELECTED_DATA_LABEL = 'Selected data'
    UNKNOWN_LABEL = 'Unknown'


class Model:
    """Manages the data and business logic for EELS visualization."""
    
    def __init__(self, dataset: xr.Dataset):
        """
        Initialize the model with dataset.
        
        Args:
            dataset: xarray Dataset containing EELS data with dimensions x, y, and Eloss
        """
        self.dataset = dataset
        self.dataset_type: Optional[str] = None
        self.hover_limits: Optional[Tuple[float, float, float, float]] = None
        self.x_limits: Optional[Tuple[float, float]] = None
        self.y_limits: Optional[Tuple[float, float]] = None
        self.empty_curve_dataset: Optional[xr.Dataset] = None
        
        # Analyze dataset and set initial state
        self._analyze_dataset()
        self._create_empty_curve_dataset()
        
    def _analyze_dataset(self) -> None:
        """Analyze the dataset to determine its type and dimensions."""
        x_size = self.dataset.x.values.size
        y_size = self.dataset.y.values.size
        
        if x_size == 1 and y_size == 1:
            self.dataset_type = Constants.SINGLE_SPECTRUM
        elif x_size == 1 and y_size != 1:
            self.dataset_type = Constants.SPECTRUM_LINE
            self._set_hover_limits_1d()
        elif x_size != 1 and y_size != 1:
            self.dataset_type = Constants.SPECTRUM_IMAGE
            self._calculate_display_limits(x_size, y_size)
            self._set_hover_limits_2d()
    
    def _create_empty_curve_dataset(self) -> None:
        """Create an empty curve dataset for display purposes."""
        electron_count_data = {
            Constants.ELECTRON_COUNT: ([Constants.ELOSS], np.zeros_like(self.dataset.Eloss.values))
        }
        coordinate_data = {Constants.ELOSS: self.dataset.Eloss.values}
        self.empty_curve_dataset = xr.Dataset(electron_count_data, coords=coordinate_data)
    
    def _set_hover_limits_1d(self) -> None:
        """Set hover limits for spectrum line visualization."""
        self.hover_limits = (
            self.dataset.Eloss.values[0] - 0.5,
            self.dataset.Eloss.values[-1] + 0.5,
            self.dataset.y.values[0] - 0.5,
            self.dataset.y.values[-1] + 0.5
        )
    
    def _set_hover_limits_2d(self) -> None:
        """Set hover limits for spectrum image visualization."""
        self.hover_limits = (
            self.dataset.x.values[0] - 0.5,
            self.dataset.x.values[-1] + 0.5,
            self.dataset.y.values[0] - 0.5,
            self.dataset.y.values[-1] + 0.5
        )
    
    def _calculate_display_limits(self, x_size: int, y_size: int) -> None:
        """Calculate display limits to maintain aspect ratio for spectrum images."""
        size_difference = abs(y_size - x_size)
        
        if x_size < y_size:
            self.x_limits = (-0.5 - size_difference / 2, x_size - 0.5 + size_difference / 2)
            self.y_limits = (-0.5, y_size - 0.5)
        else:
            self.y_limits = (-0.5 - size_difference / 2, y_size - 0.5 + size_difference / 2)
            self.x_limits = (-0.5, x_size - 0.5)
    
    def get_dataset_name(self) -> str:
        """Safely get the original dataset name."""
        try:
            original_name = self.dataset.original_name
        except AttributeError:
            original_name = getattr(self.dataset, 'attrs', {}).get('original_name', UIConfig.UNKNOWN_LABEL)
        
        # Ensure original_name is always a string
        if not isinstance(original_name, str):
            original_name = str(original_name)
            
        return original_name
    
    def is_point_in_bounds(self, x: float, y: float) -> bool:
        """Check if a point is within the hover limits."""
        if self.hover_limits is None:
            return True
        
        x_min, x_max, y_min, y_max = self.hover_limits
        return not (x >= x_max or x <= x_min or y >= y_max or y <= y_min)