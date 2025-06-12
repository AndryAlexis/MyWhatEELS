from .what_eels import app as what_eels_app

def create_apps():

    APPS = {
        "Feature 1": what_eels_app(), 
    }

    return APPS