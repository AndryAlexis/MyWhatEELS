import panel as pn

def home():
    return pn.template.FastListTemplate(
        title="Home Page",
        main=[pn.pane.Markdown("# Home Page")],
    )

def about():
    return pn.template.FastListTemplate(
        title="About Page",
        main=[pn.pane.Markdown("# About Page")],
    )

pn.serve(
    {
        "/": home,
        "/about": about,
    },
    title="My Multi-Page Panel App"
)