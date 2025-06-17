import panel as pn

pn.extension('filedropper', raw_css=[
    """
        .bk-panel-models-file_dropper-FileDropper {
            border: 2px dashed #ccc;
            padding: 0px;
            text-align: center;
            width: 100%;
            height: 67px;
        }
    """
])

def app(title="Application Title"):
    menu_items = [('Option A', 'a'), ('Option B', 'b'), ('Option C', 'c'), None, ('Help', 'help')]

    top_menu = pn.Row(
        pn.widgets.Button(name='Cuantificacion', button_type='primary'),
        pn.widgets.Button(name='Clustering', button_type='primary'),
        pn.widgets.Button(name='NLLS', button_type='primary'),
        pn.widgets.MenuButton(name='Test mientras Vanessa piensa', button_type='primary', items=menu_items),
    )

    # Create FileDropper and output pane
    file_dropper = pn.widgets.FileDropper(
        layout="compact",
        multiple=False,
    )
    file_name_pane = pn.pane.Markdown("No file uploaded yet.", sizing_mode='stretch_width')

    # Callback to update file name in main area
    def on_files_change(event):
        files = event.new

        if files:
            for file in files:
                if isinstance(file, dict):
                    file_name_pane.object = f"**Uploaded file:** {file.get('name')}"
                    break
                else:
                    file_name_pane.object = f"**Uploaded file:** {file}"
        else:
            file_name_pane.object = "No file uploaded yet."

    file_dropper.param.watch(on_files_change, 'value')

    # Instantiate the template with widgets displayed in the sidebar
    template = pn.template.FastListTemplate(
        title=title,
        sidebar=[
            file_dropper,
            pn.pane.Markdown(
                """
                ## Sidebar
                This is a placeholder for the sidebar content.
                You can add widgets, controls, or any other content here.
                """,
                sizing_mode='stretch_width',
            ),
        ],
        header=[top_menu],
    )

    # Show file name in main area
    template.main.append(file_name_pane)
    template.main.append(
        pn.pane.Markdown(
            """
                # Welcome to WhatEELS
                This is a placeholder for the main content of the application.
                You can add your main application content here.
            """,
            sizing_mode='stretch_width',
        )
    )

    return template