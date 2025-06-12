import panel as pn

pn.extension()

# Simple Panel app using only built-in components
layout = pn.Column(
    pn.pane.Markdown("## Simple Panel Components Example"),
    pn.widgets.TextInput(name="Your Name", placeholder="Type your name..."),
    pn.widgets.IntSlider(name="Value", start=0, end=100, value=50),
    pn.widgets.Button(name="Click Me", button_type="primary"),
)

layout.servable()
