from .features import feature_0, feature_1


def app():
    """Create a Panel application with multiple features.
    Returns:
        dict: A dictionary mapping feature names to their corresponding Panel components.
    """

    FEATURES = {
        "0": feature_0,
        "1": feature_1,
        # Add more features here as needed
    }
    return FEATURES
