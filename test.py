import panel as pn
from panel.template import FastListTemplate
import numpy as np
xarray = None
try:
    import xarray
except ImportError:
    pass

# Import the visualizer
from whateels.pages.home.MVC.view.eels_plots.spectrum_image_visualizer import SpectrumImageVisualizer

# Dummy model for demonstration
class DummyColors:
    ROYALBLUE = '#4169e1'
    CRIMSON = '#dc143c'
    LIGHTSALMON = '#ffa07a'

class DummyConstants:
    ELOSS = 'energy_loss'
    AXIS_X = 'x'
    AXIS_Y = 'y'

class DummyDataset:
    def __init__(self):
        # Create a small 3D datacube: (y, x, energy_loss)
        self.ElectronCount = np.random.rand(10, 10, 50)
        self.coords = {
            'energy_loss': np.linspace(0, 100, 50),
            'x': np.arange(10),
            'y': np.arange(10)
        }

class DummyModel:
    def __init__(self):
        self.colors = DummyColors()
        self.constants = DummyConstants()
        self.dataset = DummyDataset()


# --- FileDropper Integration ---
from whateels.components.file_dropper import FileDropper

# State to hold uploaded file
uploaded_file_data = {}


# Reference to visualizer and model for updating
model = DummyModel()
visualizer = SpectrumImageVisualizer(model)
layout = visualizer.create_layout()

def on_file_uploaded(filename, file_content):
    uploaded_file_data['filename'] = filename
    uploaded_file_data['file_content'] = file_content
    # DEMO: Replace DummyDataset with uploaded file content if possible
    # For real use, parse DM3/DM4 file here
    try:
        # Try to interpret as a numpy array (for demo, expects .npy file)
        import io
        arr = np.load(io.BytesIO(file_content))
        # Assume arr is (y, x, energy_loss)
        model.dataset.ElectronCount = arr
        model.dataset.coords = {
            'energy_loss': np.linspace(0, 100, arr.shape[2]),
            'x': np.arange(arr.shape[1]),
            'y': np.arange(arr.shape[0])
        }
        # Update visualizer's axis and layout
        visualizer.e_axis = model.dataset.coords[model.constants.ELOSS]
        visualizer.clean_dataset = None
        visualizer.image = None
        visualizer._setup_plots()
        layout[2] = visualizer.spectrum_pane
        layout[1] = visualizer.image
        print(f"Dataset updated from uploaded file: {filename}")
    except Exception as e:
        print(f"Failed to parse uploaded file: {e}")
    print(f"File uploaded: {filename} ({len(file_content)} bytes)")

def on_file_removed(filename):
    uploaded_file_data.clear()
    print(f"File removed: {filename}")

file_dropper = FileDropper(
    on_file_uploaded_callback=on_file_uploaded,
    on_file_removed_callback=on_file_removed,
)

# Instantiate the visualizer (still uses dummy data)
model = DummyModel()
visualizer = SpectrumImageVisualizer(model)
layout = visualizer.create_layout()

# Create the Panel app template
template = FastListTemplate(
    title="Spectrum Image Visualizer Demo",
    sidebar=[file_dropper],
    main=[layout],
)

template.servable()
