import panel as pn

pn.extension(sizing_mode="stretch_width")

from .what_eels import app as what_eels_app

THUMBNAIL_PATH = "apps/what_eels/WhatEELS.jpg"

def create_apps():

    def test_app():
        return pn.Column(
            "TestApp", "Welcome to the test app",
            pn.pane.JPG(THUMBNAIL_PATH)
        )

    APPS = {
        "TestApp": test_app,
        "WhatEELS": what_eels_app, 
    }

    # return pn.serve(APPS, port=5006)
    return pn.Column(
        "TestApp", "Welcome to the test app",
        pn.pane.JPG(THUMBNAIL_PATH)
    )

create_apps().servable()