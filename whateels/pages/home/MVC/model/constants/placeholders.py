from pathlib import Path

class Placeholders:
    
    _HTML_DIR = Path(__file__).parents[5] / "assets" / "html"
    
    @staticmethod
    def _load_html_template(filename: str) -> str:
        """Load an HTML template from a file"""
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    NO_FILE_LOADED = _load_html_template(str(_HTML_DIR / "no_file_loaded.html"))
    LOADING_FILE = _load_html_template(str(_HTML_DIR / "loading_file.html"))
    ERROR_FILE = _load_html_template(str(_HTML_DIR / "error_file.html"))