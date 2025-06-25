import panel as pn
pn.extension()

# Load custom CSS for FastListTemplate
pn.config.raw_css.append(open("whateels/assets/css/fastlisttemplate.css").read())

def fast_list_template(title, main, sidebar=None, header=None):
    if header is None:
        header = [
        pn.pane.Markdown("[NLLS](/nlls)", css_classes=["fast-list-header"]),
        pn.pane.Markdown("[Home](/)", css_classes=["fast-list-header"]),
        pn.pane.Markdown("[Login](/login)", css_classes=["fast-list-header"]),
    ]
    """
    Create a FastListTemplate with the given title, main content, sidebar content, and header content.
    
    Args:
        title (str): The title of the template.
        main_content (list): List of Panel components for the main content.
        sidebar_content (list, optional): List of Panel components for the sidebar. Defaults to None.
        header_content (list, optional): List of Panel components for the header. Defaults to None.
    
    Returns:
        pn.template.FastListTemplate: The configured FastListTemplate.
    """
    return pn.template.FastListTemplate(
        title=title,
        main=main,
        sidebar=sidebar,
        header=header
    )