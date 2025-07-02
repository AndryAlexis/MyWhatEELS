import os
import panel as pn

class LoadCSS:
    """
    A singleton class to load CSS files into the Panel configuration.
    This ensures CSS files are loaded only once, even if the class is instantiated multiple times.
    """
    
    _instance = None
    _css_loaded = False
    
    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern: Ensure only one instance exists.
        This method is called BEFORE __init__ when creating an object.
        
        Args:
            *args, **kwargs: Accept any arguments (they'll be passed to __init__)
        """
        if cls._instance is None:
            cls._instance = super(LoadCSS, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, css_files=None):
        """
        Initialize the LoadCSS instance.
        Only loads CSS on the first instantiation due to the _css_loaded flag.
        
        Args:
            css_files: None or a list/tuple of CSS file paths (strings)
        
        Raises:
            TypeError: If css_files is not None, list, or tuple
            TypeError: If any item in css_files is not a string
        """
        # Validate css_files parameter using explicit type checking
        if css_files is not None:
            # More explicit type checking using isinstance with type objects
            if not isinstance(css_files, (list, tuple)):
                actual_type = type(css_files).__name__
                raise TypeError(f"css_files must be None, list, or tuple; got {actual_type}")
            
            # Check that all items are strings
            for i, css_file in enumerate(css_files):
                if not isinstance(css_file, str):
                    raise TypeError(f"css_files[{i}] must be a string, got {type(css_file).__name__}")
        
        # Only load CSS once, even if __init__ is called multiple times
        if not LoadCSS._css_loaded:
            self._load_css(css_files)
            LoadCSS._css_loaded = True
    
    def _load_css(self, css_files=None):
        """
        Load CSS files for the application.
        
        Args:
            css_files: List/tuple of CSS file paths, or None to use defaults
        """
        # Use provided css_files or fall back to default files
        if css_files is None:
            css_files = [
                "whateels/assets/css/custom_page.css",
                "whateels/assets/css/home.css"
            ]
        
        for css_file in css_files:
            try:
                if os.path.exists(css_file):
                    with open(css_file, "r", encoding="utf-8") as f:
                        pn.config.raw_css.append(f.read())
                    print(f"✅ Loaded CSS: {css_file}")
                else:
                    print(f"⚠️  CSS file not found: {css_file}")
            except Exception as e:
                print(f"❌ Error loading CSS {css_file}: {e}")


# Usage example:
# css_loader1 = LoadCSS()  # Loads CSS
# css_loader2 = LoadCSS()  # Same instance, doesn't reload CSS
# print(css_loader1 is css_loader2)  # True - same object