import panel as pn

def file_dropper():
    pn.extension('filedropper')
    
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
    
    return file_dropper, file_name_pane