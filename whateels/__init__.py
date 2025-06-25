import panel as pn

from whateels.pages import home, nlls, login

def app(title="WhatEELS"):
    pn.extension()
    
    pages = {
        "/": home,
        "/nlls": nlls,
        "/login": login
    }

    return pn.serve(
        pages,
        title=title,
        port=5006  # Set your desired port here
    )