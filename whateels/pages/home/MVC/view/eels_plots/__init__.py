"""
Visualization factories for different EELS data types.
"""

from .spectrum_image_visualizer import SpectrumImageVisualizer
from .spectrum_line_visualizer import SpectrumLineVisualizer

__all__ = [
    'SpectrumLineVisualizer', 
    'SpectrumImageVisualizer'
]
