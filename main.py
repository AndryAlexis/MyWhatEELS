import panel as pn
pn.extension(sizing_mode="stretch_width") # Import Panel and initialize the extension

import whateels

if __name__ == "__main__":
    pn.serve(whateels.app(), port=5006)