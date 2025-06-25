import panel as pn
pn.extension()

from whateels.components import fast_list_template

def nlls():
    return fast_list_template(
        title="NLLS",
        main=[pn.pane.Markdown("# NLLS Page")],
        sidebar=[],
    )