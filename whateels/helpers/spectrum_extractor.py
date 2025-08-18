class SpectrumExtractor:
    @staticmethod
    def get_spectrum_from_pixel(model, i, j):
        """Extract spectrum from a pixel (i, j) in the model's dataset."""
        try:
            spec = self._da.values[int(i), int(j), :].astype(float)
            return spec
        except Exception:
            # Try alternative indexing order (x,y,E) if needed
            try:
                spec = self._da.values[int(j), int(i), :].astype(float)
                return spec
            except Exception:
                return np.zeros(self._energy.shape)
        pass

    @staticmethod
    def get_spectrum_from_indices(model, pairs):
        """Extract spectrum from a list of indices (pairs) in the model's dataset."""
        # Implementation goes here
        pass

    @staticmethod
    def extract_point(data):
        """Process a single point's data."""
        # Implementation goes here
        pass

    @staticmethod
    def extract_region(data):
        """Process a region's data."""
        # Implementation goes here
        pass
