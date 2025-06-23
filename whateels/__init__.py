import panel as pn
pn.extension()

from whateels.pages import home_main_area, home_sidebar_area, nlls_main_area, nlls_sidebar_area
from whateels.components import top_menu as tm

def app(title="Application Title"):
    main_area = pn.Column()
    sidebar_area = pn.Column()

    def update_main_area(event=None):
        page = pn.state.location.hash.lstrip("#")
        if page == "nlls":
            main_area[:] = [nlls_main_area()]
        else:
            main_area[:] = [home_main_area()]
            
    def update_sidebar_area(event=None):
        page = pn.state.location.hash.lstrip("#")
        if page == "nlls":
            sidebar_area[:] = [nlls_sidebar_area()]
        else:
            sidebar_area[:] = [home_sidebar_area()]

    # Initial load
    update_main_area()
    update_sidebar_area()
    
    # Watch for URL hash changes
    pn.state.location.param.watch(lambda e: update_main_area(), "hash")
    pn.state.location.param.watch(lambda e: update_sidebar_area(), "hash")

    # Instantiate the template with widgets displayed in the sidebar
    template = pn.template.FastListTemplate(
        title=title,
        sidebar=[sidebar_area],
        main=[main_area],
        header=[tm()]
    )

    return template