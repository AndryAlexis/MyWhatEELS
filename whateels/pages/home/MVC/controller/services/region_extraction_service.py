class RegionExtractionService:
    """
    Service for extracting points and regions from Plotly event payloads.
    """

    @staticmethod
    def extract_point(data):
        """
        Extract (x, y) from hover_data/click_data style Plotly (heatmap or scatter).
        """
        try:
            if not data or "points" not in data or not data["points"]:
                return None
            p = data["points"][0]
            return {"x": p.get("x"), "y": p.get("y"), "curve": p.get("curveNumber", None)}
        except Exception:
            return None

    @staticmethod
    def extract_region(data):
        """
        From selected_data → list of (i, j). Accepts selection from any trace (takes x, y).
        """
        try:
            if not data or "points" not in data or not data["points"]:
                return []
            pairs = []
            for p in data["points"]:
                x = p.get("x")
                y = p.get("y")
                if x is None or y is None:
                    continue
                pairs.append((int(y), int(x)))
            # Remove duplicates preserving order
            pairs = list(dict.fromkeys(pairs))
            return pairs
        except Exception:
            return []
