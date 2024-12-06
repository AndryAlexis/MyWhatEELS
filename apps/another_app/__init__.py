import panel as pn

pn.extension(sizing_mode="stretch_width")

def app():
    pages = {
        "Page 1": pn.Column("# Page 1", "...bla bla bla"),
        "Page 2": pn.Column("# Page 2", "...more bla"),
    }

    def show(page):
        return pages[page]

    starting_page = pn.state.session_args.get("page", [b"Page 1"])[0].decode()
    page = pn.widgets.RadioButtonGroup(
        value=starting_page,
        options=list(pages.keys()),
        name="Page",
        sizing_mode="fixed",
        button_type="success",
    )
    ishow = pn.bind(show, page=page)
    pn.state.location.sync(page, {"value": "page"})

    ACCENT_COLOR = "#0072B5"
    DEFAULT_PARAMS = {
        "site": "WhatEELS",
        "accent_base_color": ACCENT_COLOR,
        "header_background": ACCENT_COLOR,
    }
    
    return pn.template.FastListTemplate(
        title="",
        sidebar=[page],
        main=[ishow],
        **DEFAULT_PARAMS,
    ).servable()
    
# app().servable()
    