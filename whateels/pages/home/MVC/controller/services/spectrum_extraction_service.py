import numpy as np

class SpectrumExtractionService:
    """
    Service for extracting and summing spectra from an EELS datacube.
    """

    def __init__(self, datacube: np.ndarray, energy_axis: np.ndarray):
        self._da = datacube
        self._energy = energy_axis

    def spectrum_from_pixel(self, i, j):
        """
        Extract the spectrum for a given pixel (i, j) from the datacube.
        Returns a 1D numpy array of intensities.
        """
        try:
            spec = self._da[int(i), int(j), :].astype(float)
            return spec
        except Exception:
            try:
                spec = self._da[int(j), int(i), :].astype(float)
                return spec
            except Exception:
                return np.zeros(self._energy.shape)

    def spectrum_from_indices(self, pairs):
        """
        Sum spectra for a list of (i, j) pixel pairs from the datacube.
        Returns the summed spectrum and the number of pixels.
        """
        if not pairs:
            return None
        try:
            ii, jj = zip(*pairs)
            block = self._da[np.asarray(ii), np.asarray(jj), :]
            return block.sum(axis=0), len(pairs)
        except Exception:
            try:
                ii, jj = zip(*pairs)
                block = self._da[np.asarray(jj), np.asarray(ii), :]
                return block.sum(axis=0), len(pairs)
            except Exception:
                return None
