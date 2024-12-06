import panel as pn

def home_view():
    sidebar = pn.Column(
        pn.widgets.TextInput(name="Input", placeholder="Enter text here..."),
        stylesheets=["""
            :host {
                border: 2px solid red;
                width: clamp(200px, 100%, 400px);
                overflow-y: auto;
                height: 100%;
            }
        """],
    )
    
    main = pn.Column(
        pn.widgets.TextInput(name="Input", placeholder="Enter text here..."),
    )
    
    flexbox = pn.FlexBox(sidebar, main, align_items="center", flex_wrap="nowrap", stylesheets=["""
        :host {
            height: 100%;
            border: 2px solid blue;
            
            > div {
                border: 2px solid green;
            }
        }
    """])


    return flexbox
