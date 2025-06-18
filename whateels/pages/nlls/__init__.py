import panel as pn
pn.extension()

def nlls_main_area():
    return pn.pane.Markdown("# NLLS Analysis\nThis is the NLLS page aaa.")

def nlls_sidebar_area():
    return pn.Column(
        pn.pane.Markdown("NLLS Analysis Sidebar"),
        sizing_mode='stretch_width'
    )