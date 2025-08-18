import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from xarray import Dataset
    from param.parameterized import Event
 
class SpectrumExtractor:
    @staticmethod
    def get_spectrum_from_pixel(electron_count_data: "Dataset", i: int, j: int) -> np.ndarray:
        """
        Extract the spectrum for a single pixel (i, j) from the electron_count_data cube.
        Parameters:
            electron_count_data: xarray.DataArray
                The 3D data cube containing electron counts (shape: y, x, energy).
            i: int
                Row index (y coordinate).
            j: int
                Column index (x coordinate).
        Returns:
            np.ndarray: 1D array of spectrum values for the selected pixel.
        """
        try:
            spec = electron_count_data.values[int(i), int(j), :].astype(float)
            return spec
        except Exception:
            # Try alternative indexing order (x,y,E) if needed
            try:
                spec = electron_count_data.values[int(j), int(i), :].astype(float)
                return spec
            except Exception:
                return np.zeros(electron_count_data.shape[-1])

    @staticmethod
    def get_spectrum_from_indices(electron_count_data: "Dataset", pairs):
        """Extract spectrum from a list of indices (pairs) in the model's dataset."""
        if not pairs:
            return None
        try:
            ii, jj = zip(*pairs)
            block = electron_count_data.values[np.asarray(ii), np.asarray(jj), :]  # (N, nE)
            return block.sum(axis=0), len(pairs)
        except Exception:
            # attempt swap if indexing order different
            try:
                ii, jj = zip(*pairs)
                block = electron_count_data.values[np.asarray(jj), np.asarray(ii), :]
                return block.sum(axis=0), len(pairs)
            except Exception:
                return None

    @staticmethod
    def extract_point(event: "Event"):
        """Process a single point's data."""
        point_data = event.new
        try:
            if not point_data or "points" not in point_data or not point_data["points"]:
                return None
            p = point_data["points"][0]
            return {"x": p.get("x"), "y": p.get("y"), "curve": p.get("curveNumber", None)}
        except Exception:
            return None

    @staticmethod
    def extract_region(data):
        """Process a region's data."""
        # Implementation goes here
        pass
