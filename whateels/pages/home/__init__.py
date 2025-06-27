import panel as pn
pn.extension()

pn.config.raw_css.append(open("whateels/assets/css/home.css").read())

from whateels.components import file_dropper as fd, fast_list_template

def home():
    file_dropper_widget, feedback_message_pane = fd()
    
    fdw_box_title = pn.pane.HTML(
        "<h3 class='fdw-box-title'>Upload an image</h3>",
    )
    
    fdw_box = pn.WidgetBox(
        fdw_box_title, 
        file_dropper_widget, 
        feedback_message_pane,
    )

    return fast_list_template(
        title="WhatEELS",
        main=[pn.pane.Markdown("# Home Page")],
        sidebar=[
            fdw_box
        ],
    )