"""
Visualization factories for different EELS data types.
"""

from .spectrum_line_visualizer import SpectrumLineVisualizer
from .spectrum_image_visualizer import SpectrumImageVisualizer

__all__ = [
    'SpectrumLineVisualizer', 
    'SpectrumImageVisualizer'
]
