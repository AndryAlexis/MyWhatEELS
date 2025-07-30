import panel as pn, holoviews as hv, traceback

from .eels_plot_factory import EELSPlotFactory
from whateels.components import FileDropper
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class View:
    """
    View class for the home page of the WhatEELS application.

    Responsibilities:
    - Render and manage the UI layout and state transitions (placeholders, loading, error, plots)
    - Instantiate and expose UI components (sidebar, file dropper, main area)
    - Coordinate with EELS plot factories for visualization
    - Expose properties for Controller to interact with UI elements

    The View does not make business logic decisions; it only renders what the Controller instructs.
    """

    # --- Class-level constants ---
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'

    # --- Initialization ---
    def __init__(self, model: "Model"):
        self.model = model
        self.eels_plot_factory = None
        self._main_container_layout = None
        self._sidebar_container_layout = None
        self._loading_placeholder = None
        self._no_file_placeholder = None
        self._error_placeholder = None
        self._active_plotter = None
        self._last_dataset_info_component = None
        self._file_dropper = None
        
        self._init_visualization_components()

    # --- Properties ---

    @property
    def sidebar(self) -> pn.viewable.Viewable:
        """Sidebar layout containing the file dropper and additional controls."""
        return self._sidebar_container_layout


    @property
    def main(self) -> pn.Column:
        """Main content area layout for displaying plots or placeholders."""
        return self._main_container_layout


    @property
    def loading_placeholder(self) -> pn.pane.HTML:
        """HTML placeholder shown while a file is being processed."""
        return self._loading_placeholder


    @property
    def no_file_placeholder(self) -> pn.pane.HTML:
        """HTML placeholder shown when no file is loaded."""
        return self._no_file_placeholder


    @property
    def error_placeholder(self) -> pn.pane.HTML:
        """HTML placeholder shown when an error occurs."""
        return self._error_placeholder


    @property
    def file_dropper(self) -> FileDropper:
        """FileDropper widget for file upload interactions."""
        return self._file_dropper
    

    @property
    def active_plotter(self):
        """The currently active plotter/visualizer instance (set after file upload)."""
        return self._active_plotter


    @property
    def last_dataset_info_component(self) -> pn.viewable.Viewable:
        """Reference to the last dataset info component added to the sidebar."""
        return self._last_dataset_info_component


    @last_dataset_info_component.setter
    def last_dataset_info_component(self, component: pn.viewable.Viewable):
        """Set the last dataset info component (must be a Panel Viewable or None)."""
        if component is not None and not isinstance(component, pn.viewable.Viewable):
            raise ValueError("Component must be a Panel Viewable")
        self._last_dataset_info_component = component
        

    @active_plotter.setter
    def active_plotter(self, plotter):
        """Set the active plotter/visualizer instance."""
        self._active_plotter = plotter


    @property
    def tap_stream(self):
        """Return the tap stream from the active plotter, if available."""
        if self._active_plotter and hasattr(self._active_plotter, 'tap_stream'):
            return self._active_plotter.tap_stream
        return None


    @property
    def spectrum_pane(self):
        """Return the spectrum pane from the active plotter, if available."""
        if self._active_plotter and hasattr(self._active_plotter, 'spectrum_pane'):
            return self._active_plotter.spectrum_pane
        return None

    # --- Private/Internal Setup Methods ---

    def _init_visualization_components(self):
        """
        Initialize main visualization container and placeholders.

        Sets up:
        - no_file_placeholder: shown when no file is loaded
        - loading_placeholder: shown during file processing
        - error_placeholder: shown when an error occurs
        - sidebar and main layout containers
        """
        self._no_file_placeholder = pn.pane.HTML(
            self.model.placeholders.NO_FILE_LOADED,
            sizing_mode=self._STRETCH_BOTH
        )
        self._loading_placeholder = pn.Column(
            pn.pane.HTML(
                self.model.placeholders.LOADING_FILE,
                sizing_mode=self._STRETCH_BOTH
            ),
            sizing_mode=self._STRETCH_BOTH,
        )
        self._error_placeholder = pn.pane.HTML(
            self.model.placeholders.ERROR_FILE,
            sizing_mode=self._STRETCH_BOTH
        )
        self._sidebar_container_layout = self._sidebar_layout()
        self._main_container_layout = self._main_layout()

    def _sidebar_layout(self):
        file_dropper = FileDropper(
            valid_extensions=self.model.file_dropper.VALID_EXTENSIONS,
            reject_message=self.model.file_dropper.REJECT_MESSAGE,
            success_message=self.model.file_dropper.SUCCESS_MESSAGE,
            feedback_message=self.model.file_dropper.FEEDBACK_MESSAGE,
        )
        self._file_dropper = file_dropper
        self._sidebar_container_layout = pn.Column(
            self._file_dropper,
            pn.layout.Divider(),
            pn.Spacer(height=10),
            sizing_mode=self._STRETCH_WIDTH
        )
        return self._sidebar_container_layout

    def _main_layout(self):
        self._main_container_layout = pn.Column(
            self._no_file_placeholder,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout

    def show_single_spectrum(self, visualizer):
        spectrum_data = visualizer.get_spectrum_data()
        spectrum_curve = hv.Curve(
            spectrum_data,
            kdims=[self.model.constants.ELOSS],
            vdims=[self.model.constants.ELECTRON_COUNT]
        ).opts(
            width=800,
            height=400,
            color=self.model.colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='EELS Spectrum'
        )
        spectrum_pane = pn.pane.HoloViews(spectrum_curve, sizing_mode=self._STRETCH_WIDTH)
        self.update_main_layout(
            pn.Column(
                spectrum_pane,
                sizing_mode=self._STRETCH_BOTH
            )
        )