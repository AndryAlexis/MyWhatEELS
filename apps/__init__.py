import panel as pn

from .what_eels import app as what_eels_app

def create_apps():

    def test_app():
        return pn.Column(
            "TestApp", "Welcome to the test app",
        )

    APPS = {
        "TestApp": test_app,
        "WhatEELS": what_eels_app, 
    }

    return APPS