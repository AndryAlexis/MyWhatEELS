import panel as pn

def home_page():
    return pn.pane.Markdown("# Welcome to WhatEELS")

def nlls_page():
    return pn.pane.Markdown("# NLLS Analysis\nThis is the NLLS page.")

main_area = pn.Column()

def update_main_area(event=None):
    page = pn.state.location.hash.lstrip("#")
    if page == "nlls":
        main_area[:] = [nlls_page()]
    else:
        main_area[:] = [home_page()]

# Initial load
update_main_area()

# Watch for URL hash changes
pn.state.location.param.watch(lambda e: update_main_area(), "hash")

# Navigation buttons
nav = pn.Row(
    pn.widgets.Button(
        name="Home", button_type="primary", width=100, 
        on_click=lambda e: setattr(pn.state.location, "hash", "#home"),
    ),
    pn.widgets.Button(
        name="NLLS", button_type="primary", width=100,
        on_click=lambda e: setattr(pn.state.location, "hash", "#nlls")
    ),
)

template = pn.template.FastListTemplate(
    title="WhatEELS",
    sidebar=[nav],
    main=[main_area],
)

# In your main.py or serve entry point:
template.servable()