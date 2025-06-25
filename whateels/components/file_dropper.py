import panel as pn
pn.extension()
import os

def file_dropper():    
    # Create FileDropper and output pane
    file_dropper = pn.widgets.FileDropper(
        sizing_mode='stretch_width',  # Make it stretch to available width
        multiple=False,  # Allow only single file upload
    )
    file_name_pane = pn.pane.Markdown("No file uploaded yet.", sizing_mode='stretch_width')

    # Callback to update file name in main area
    def on_files_change(event): 
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file(s) to the uploads directory
        # file_dropper.value is a dict: {filename: bytes}
        for file_name, file_bytes in file_dropper.value.items():
            if not (file_name.lower().endswith('.dm3') or file_name.lower().endswith('.dm4')):
                # Reset the FileDropper by clearing its value and triggering UI refresh
                file_dropper.value = {}
                file_dropper.param.trigger('value')  # Force UI update
                print(f"Rejected file: {file_name} (not .dm3 or .dm4)")
                file_name_pane.object = f"❌ Rejected file: {file_name} (not .dm3 or .dm4)"
                continue
            file_path = os.path.join("uploads", file_name)
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            print(f"File name: {file_name}, File size: {len(file_bytes) if file_bytes else 0} bytes")
            file_name_pane.object = f"✅ Uploaded file: {file_name} ({len(file_bytes)} bytes)"

    file_dropper.param.watch(on_files_change, 'value')
    
    return file_dropper, file_name_pane