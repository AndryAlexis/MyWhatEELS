# Generic file reader function
def _read_file(path):
    with open(path, "r") as file:
        return file.read()

# Helper function to generate error CSS
# Creates a red background with centered error message overlay
def _layout_error(message):
    return """
        :host :where(*) {
            color: white !important;
            background-color: red !important;
        }

        :host {
            position: relative;
        }

        :host::after {
            content: \"""" + message + """\";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2rem;
            z-index: 9999;
            pointer-events: none;
            font-weight: bold;
            text-align: center;
        }
    """

# Reads CSS files with error handling
# Returns CSS content or error styling if file cannot be read
def read_css(path):
    try:
        return _read_file(path)
    except FileNotFoundError:
        return _layout_error("CSS NOT FOUND")
    except Exception as e:
        return _layout_error("CSS ERROR")