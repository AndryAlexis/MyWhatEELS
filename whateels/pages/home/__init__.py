import panel as pn
pn.extension()

from whateels.components import file_dropper as fd, fast_list_template

def home():
    file_dropper_widget, file_name_pane = fd()

    return fast_list_template(
        title="WhatEELS",
        main=[pn.pane.Markdown("# Home Page")],
        sidebar=[
            file_dropper_widget,
            file_name_pane,
        ],
    )