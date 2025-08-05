"""
EELSPlotFactory: Centralized factory for creating EELS visualizer components based on dataset type.

Features:
- Uses the Factory Pattern to decouple visualization creation from the View.
- Supports extensible mapping of dataset types to visualizer classes.
- Provides a consistent interface for visualization components.
- Handles errors robustly by raising exceptions with clear messages.
"""

from ..view.eels_plots import SpectrumLineVisualizer, SpectrumImageVisualizer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model import Model
    from ..controller import Controller

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
    
    def __init__(self, model: "Model", controller: "Controller") -> None:
        self._model = model
        self._controller = controller
        
        # Mapping of dataset types to visualizer classes
        # This can be extended with more visualizers as needed
        self._all_spectrum_visualizer = {
            model.constants.SPECTRUM_LINE: SpectrumLineVisualizer,
            model.constants.SPECTRUM_IMAGE: SpectrumImageVisualizer,
            model.constants.SINGLE_SPECTRUM: SpectrumLineVisualizer,  # TODO Assuming single spectrum uses line visualizer
        }
    
    def choose_spectrum(self, dataset_type: str) -> SpectrumLineVisualizer | SpectrumImageVisualizer | None:
        """
        Instantiates and returns the appropriate EELS visualizer for the specified dataset type.

        Args:
            dataset_type (str): The dataset type key (e.g., model.constants.SPECTRUM_LINE or SPECTRUM_IMAGE).

        Returns:
            SpectrumLineVisualizer | SpectrumImageVisualizer: An instance of the corresponding visualizer class.

        Raises:
            ValueError: If the dataset type is not recognized (not mapped in _all_spectrum_visualizer).
            RuntimeError: If an exception occurs during visualizer instantiation.
        """
        try:
            chosed_spectrum_visualizer = self._all_spectrum_visualizer.get(dataset_type)
            if chosed_spectrum_visualizer:
                chosed_spectrum_visualizer = chosed_spectrum_visualizer(self._model, self._controller)
                return chosed_spectrum_visualizer
            else:
                chosed_spectrum_visualizer = None
                error_msg = self._UNKNOWN_TYPE_ERROR.format(dataset_type, list(self._all_spectrum_visualizer.keys()))
                raise ValueError(error_msg)
        except Exception as e:
            chosed_spectrum_visualizer = None
            error_msg = self._EXCEPTION_ERROR.format(dataset_type, e)
            traceback.print_exc()
            raise RuntimeError(error_msg) from e