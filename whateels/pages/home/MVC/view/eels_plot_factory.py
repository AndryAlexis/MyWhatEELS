"""
EELSPlotFactory: Centralized factory for creating EELS visualizer components based on dataset type.

Features:
- Uses the Factory Pattern to decouple visualization creation from the View.
- Supports extensible mapping of dataset types to visualizer classes.
- Provides a consistent interface for visualization components.
- Handles errors robustly by raising exceptions with clear messages.
"""

from .eels_plots import SpectrumLineVisualizer, SpectrumImageVisualizer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from . import View

import traceback

class EELSPlotFactory:
    """
    Centralized factory for creating EELS visualizer components.
    
    - Decouples visualization creation from the View.
    - Maps dataset types to visualizer classes.
    - Raises exceptions for unknown types or plot creation errors.
    """
    
    # Error message constants
    _UNKNOWN_TYPE_ERROR = "[EELSPlotFactory] Unknown dataset type: '{}'. Supported types: {}"
    _EXCEPTION_ERROR = "[EELSPlotFactory] Exception while creating plot for dataset type '{}': {}"
    
    def __init__(self, model: "Model", view: "View") -> None:
        self._model = model
        self._view = view
        self._current_spectrum_visualizer_renderer = None  # Store reference to active plotter
        self._all_spectrum_visualizer = {
            model.constants.SPECTRUM_LINE: SpectrumLineVisualizer,
            model.constants.SPECTRUM_IMAGE: SpectrumImageVisualizer
        }
    
    def create_plots(self, dataset_type: str):
        """
        Create and return an EELS plot visualizer for the given dataset type.
        
        Args:
            dataset_type (str): Type of dataset (e.g., SSp, SLi, SIm).
        
        Returns:
            Panel component with the appropriate plot visualization.
        
        Raises:
            ValueError: If the dataset type is unknown.
            RuntimeError: If an error occurs during plot creation.
        """
        try:
            chosed_spectrum_visualizer = self._all_spectrum_visualizer.get(dataset_type)
            if chosed_spectrum_visualizer:
                self._current_spectrum_visualizer_renderer = chosed_spectrum_visualizer(self._model)
                return self._current_spectrum_visualizer_renderer.create_layout()
            else:
                self._current_spectrum_visualizer_renderer = None
                error_msg = self._UNKNOWN_TYPE_ERROR.format(dataset_type, list(self._all_spectrum_visualizer.keys()))
                raise ValueError(error_msg)
        except Exception as e:
            self._current_spectrum_visualizer_renderer = None
            error_msg = self._EXCEPTION_ERROR.format(dataset_type, e)
            traceback.print_exc()
            raise RuntimeError(error_msg) from e

    @property
    def current_spectrum_visualizer_renderer(self) -> SpectrumLineVisualizer | SpectrumImageVisualizer | None:
        """
        Get the current spectrum visualizer renderer instance.
        Returns:
            The active visualizer renderer, or None if not set.
        """
        return self._current_spectrum_visualizer_renderer