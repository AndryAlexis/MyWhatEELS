class Model:
    """
    Model for the metadata page.
    Simple data storage for metadata information.
    """
    
    def __init__(self):
        pass
    
    @property
    def constants(self) -> "Constants":
        """Expose constants for the metadata page."""
        return self.Constants()

    class Constants:
        TITLE = "Eels Metadata Details"
