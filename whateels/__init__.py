import hvplot.pandas
import numpy as np
import panel as pn
import pandas as pd
import io   

pn.extension('filedropper')

def app(title="Application Title"):
    menu_items = [('Option A', 'a'), ('Option B', 'b'), ('Option C', 'c'), None, ('Help', 'help')]

    top_menu = pn.Row(
        pn.widgets.Button(name='Cuantificacion', button_type='primary'),
        pn.widgets.Button(name='Clustering', button_type='primary'),
        pn.widgets.Button(name='NLLS', button_type='primary'),
        pn.widgets.MenuButton(name='Test mientras Vanessa piensa', button_type='primary', items=menu_items),
    )

    # Instantiate the template with widgets displayed in the sidebar
    template = pn.template.FastListTemplate(
        title=title,
        sidebar=[pn.widgets.FileDropper(layout="integrated"),],
        header=[top_menu],
        right_sidebar=[
            pn.widgets.Select(
                name='Language',
                options=['English', 'Español', 'Català'],
                value='English',
                width=200
            )
        ],
    )

    # Append a layout to the main area, to demonstrate the list-like API
    template.main.append(
        pn.Row(pn.pane.Markdown("## Main Content Area"),)
    )

    return template