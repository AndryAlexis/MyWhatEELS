import panel as pn
pn.extension()

def file_dropper():    
    # Create FileDropper and output pane
    file_input = pn.widgets.FileInput(
        accept='.dm3,.dm4',  # Accept specific file types
        multiple=False,  # Allow only single file upload
        sizing_mode='stretch_width',  # Make it stretch to available width
    )
    file_name_pane = pn.pane.Markdown("No file uploaded yet.", sizing_mode='stretch_width')

    # Callback to update file name in main area
    def on_files_change(event):
        files_bytes = file_input.value
        file_name = file_input.filename
        
        print(f"File name: {file_name}, File size: {len(files_bytes) if files_bytes else 0} bytes")

    file_input.param.watch(on_files_change, 'value')
    
    return file_input, file_name_pane