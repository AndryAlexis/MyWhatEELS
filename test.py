import panel as pn
import os
import hyperspy.api as hs

pn.extension()

# Create the FileInput widget for user uploads
file_input = pn.widgets.FileInput(accept='.dm3,.dm4,.DM3', multiple=False)
output = pn.pane.Markdown("No file uploaded yet.")
parsed_data_pane = pn.pane.Markdown("", sizing_mode='stretch_width')

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

def on_file_change(event):
    if file_input.value is not None:
        file_bytes = file_input.value
        file_name = file_input.filename
        output.object = f"**Uploaded file:** {file_name} ({len(file_bytes)} bytes)"
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        # Process the file with hyperspy
        try:
            s = hs.load(file_path)
            # Display summary info about the loaded signal
            parsed_data_pane.object = f"**HyperSpy loaded signal:**\nType: {type(s)}\nMain info: {str(s)}"
        except Exception as e:
            parsed_data_pane.object = f"**Error loading with HyperSpy:** {e}"
    else:
        output.object = "No file uploaded yet."
        parsed_data_pane.object = ""

file_input.param.watch(on_file_change, 'value')

# Panel layout
app = pn.template.FastListTemplate(
    title="File Upload & HyperSpy Example",
    sidebar=[file_input],
    main=[output, parsed_data_pane],
)

app.servable()
