import panel as pn

def filedropper() -> pn.widgets.FileDropper:
    pn.extension('filedropper')
    
    # Create a FileDropper widget
    file_dropper = pn.widgets.FileDropper(
        layout="integrated", 
        styles={
            'border': '2px dashed #ccc',
            'padding': '0px',
            'text-align': 'center',
            'width': '100%',
            'height': '100%',
        },
        accepted_filetypes=['.dm3', '.dm4'],
        multiple=True,
    )

    # Callback to print selected files info
    def on_files_change(event):
        files = event.new
        print("Raw files value:", files)
        if files:
            print("Files selected:")
            for file in files:
                if isinstance(file, dict):
                    print(f"File: {file.get('name')}, Size: {file.get('size')} bytes")
                else:
                    print(f"- {file} (type: {type(file)})", event)
        else:
            print("No files selected.")

    file_dropper.param.watch(on_files_change, 'value')

    return file_dropper