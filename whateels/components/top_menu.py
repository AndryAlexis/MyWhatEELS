import panel as pn

def top_menu() -> pn.Row:
    pn.extension('filedropper')

    # Create the top menu with buttons
    top_menu = pn.Row(
        pn.widgets.Button(name='Home', button_type='primary', width=100,
            on_click=lambda e: setattr(pn.state.location, "hash", "#home"),
        ),
        pn.widgets.Button(name='Cuantificacion', button_type='primary'),
        pn.widgets.Button(name='Clustering', button_type='primary'),
        pn.widgets.Button(
            name='NLLS', 
            button_type='primary',
            on_click=lambda e: setattr(pn.state.location, "hash", "#nlls"),
        ),
        pn.widgets.MenuButton(
            name='Test mientras Vanessa piensa',
            button_type='primary',
            items=[
                ('Option A', 'a'),
                ('Option B', 'b'),
                ('Option C', 'c'),
                None,
                ('Help', 'help')
            ]
        ),
    )

    return top_menu