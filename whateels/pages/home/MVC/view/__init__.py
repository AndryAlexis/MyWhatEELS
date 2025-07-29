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
    
    This class is responsible for:
    - UI rendering and layout presentation
    - Managing UI state transitions (placeholders, loading screens, plots)
    - Coordinating with plot factories for EELS displays
    
    The View receives data from the Model and rendering commands from the Controller,
    but does not make decisions about what to display - it only renders what it's told to.
    """

    # Constants for sizing modes
    _STRETCH_WIDTH = 'stretch_width'
    _STRETCH_BOTH = 'stretch_both'

    def __init__(self, model: "Model"):
        self.model = model

        # Factory for creating EELS plots
        self.eels_plot_factory = None
        
        self._sidebar = None

        # Main layout that will switch between UI states
        self._main_container_layout = None
        self._sidebar_container_layout = None

        # Placeholders for _main_container_layout states
        self._loading_placeholder = None
        self._no_file_placeholder = None
        self._error_placeholder = None

        # Active plotter (to access interaction streams)
        self.active_plotter = None
        
        # Last dataset info component added to sidebar (for removal)
        self._last_dataset_info_component = None

        # Last float panel added to main layout (for removal)
        # self._float_panel = None
        
        self._file_dropper = None

        # Initialize UI components
        self._init_visualization_components()

    # --- Properties ---
    @property
    def sidebar(self) -> pn.viewable.Viewable:
        return self._sidebar

    @property
    def main(self) -> pn.Column:
        return self._main_layout()
    
    # @property
    # def float_panel(self) -> pn.layout.FloatPanel:
    #     return self._float_panel_modal()
    
    @property
    def file_dropper(self) -> FileDropper:
        return self._file_dropper

    @property
    def tap_stream(self):
        """Get tap stream from active plotter"""
        if self.active_plotter and hasattr(self.active_plotter, 'tap_stream'):
            return self.active_plotter.tap_stream
        return None

    @property
    def spectrum_pane(self):
        """Get spectrum pane from active plotter"""
        if self.active_plotter and hasattr(self.active_plotter, 'spectrum_pane'):
            return self.active_plotter.spectrum_pane
        return None

    # --- Private/Internal Setup Methods ---
    def _init_visualization_components(self):
        """
        Initialize main visualization container and placeholders.
        
        Creates:
        - no_file_placeholder: shown when no file loaded
        - loading_placeholder: shown during file processing  
        - main_layout: container that switches between states
        """
        # Placeholder for when no file is loaded
        self._no_file_placeholder = pn.pane.HTML(
            self.model.placeholders.NO_FILE_LOADED,
            sizing_mode=self._STRETCH_BOTH
        )
        # Loading placeholder for when file is being processed
        self._loading_placeholder = pn.Column(
            pn.pane.HTML(
                self.model.placeholders.LOADING_FILE,
                sizing_mode=self._STRETCH_BOTH
            ),
            sizing_mode=self._STRETCH_BOTH,
        )
        # Error placeholder for when an error occurs
        self._error_placeholder = pn.pane.HTML(
            self.model.placeholders.ERROR_FILE,
            sizing_mode=self._STRETCH_BOTH
        )
        
        self._sidebar = self._sidebar_layout()

    def _sidebar_layout(self):
        """Create and return the sidebar layout"""
        file_dropper = FileDropper(
            valid_extensions=self.model.file_dropper.VALID_EXTENSIONS,
            reject_message=self.model.file_dropper.REJECT_MESSAGE,
            success_message=self.model.file_dropper.SUCCESS_MESSAGE,
            feedback_message=self.model.file_dropper.FEEDBACK_MESSAGE,
        )
        
        # Store the file dropper for later access
        self._file_dropper = file_dropper

        self._sidebar_container_layout = pn.Column(
            self._file_dropper,
            pn.layout.Divider(),
            pn.Spacer(height=10),
            sizing_mode=self._STRETCH_WIDTH
        )
        return self._sidebar_container_layout

    def _main_layout(self):
        """Create and return the main content area"""
        self._main_container_layout = pn.Column(
            self._no_file_placeholder,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout
    
    # def _float_panel_modal(self):
    #     float_panel = pn.layout.FloatPanel(
    #         visible=False,  # Start hidden
    #         sizing_mode=self._STRETCH_BOTH,
    #         width=800,
    #         height=600,
    #     )
    #     self._float_panel = float_panel
        
    # def add_contain_to_float_panel(self, content: pn.viewable.Viewable, title: str = "Details"):
    #     """
    #     Add content to the FloatPanel and set its title.
        
    #     Args:
    #         content: Content to display in the FloatPanel
    #         title: Title of the FloatPanel
    #     """
    #     if not isinstance(content, pn.viewable.Viewable):
    #         raise ValueError("Content must be a Panel Viewable")
        
    #     self._float_panel.content = content
    #     self._float_panel.title = title
    #     self._float_panel.visible = True
    
    # def toggle_float_panel(self, visible: bool):
    #     """
    #     Toggle visibility of the last float panel added to the main layout.
        
    #     Args:
    #         visible: True to show, False to hide
    #     """
    #     if self._float_panel:
    #         self._float_panel.visible = visible
    #     else:
    #         raise ValueError("No float panel exists to toggle visibility")

    # --- Public UI/State Management Methods ---
    def add_component_to_sidebar(self, component):
        self._sidebar_container_layout.append(component)

    def remove_component_from_sidebar(self, component):
        if component in self._sidebar_container_layout:
            self._sidebar_container_layout.remove(component)
        else:
            raise ValueError("Component not found in sidebar layout")

    def update_main_layout(self, plot_component):
        """Update the main area with a new plot component"""
        self._main_container_layout.clear()
        # if self._float_panel:
        #     self._main_container_layout.insert(0, self._float_panel)
        self._main_container_layout.append(plot_component)

    def show_loading(self):
        """Show loading screen while processing file"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._loading_placeholder)

    def reset_main_layout(self):
        """Reset the main area to show the placeholder, and remove the FloatPanel if present."""
        self._main_container_layout.clear()
        # if self._float_panel and self._float_panel in self._main_container_layout:
        #     self._main_container_layout.remove(self._float_panel)
        self._main_container_layout.append(self._no_file_placeholder)

    def show_error(self):
        """Show error placeholder when an error occurs"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._error_placeholder)
        
    def add_component_to_sidebar_layout(self, component: pn.viewable.Viewable):
        if not isinstance(component, pn.viewable.Viewable):
            raise ValueError("Component must be a Panel Viewable")
        self._sidebar_container_layout.append(component)
        self._last_dataset_info_component = component  # Track the last added info

    def remove_last_dataset_info_from_sidebar(self):
        if self._last_dataset_info_component and self._last_dataset_info_component in self._sidebar_container_layout:
            self._sidebar_container_layout.remove(self._last_dataset_info_component)
            self._last_dataset_info_component = None

    # --- Main Functional Methods ---
    def create_eels_plot(self, dataset_type: str):
        """
        Create EELS plots based on dataset type.
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate plot visualization, or None
            if an error occurred (in which case the view will already show an error)
        """
        self.eels_plot_factory = EELSPlotFactory(self.model, self)
        chosed_spectrum = self.eels_plot_factory.choose_spectrum(dataset_type)
        if chosed_spectrum is None:
            traceback.print_exc()
            self.show_error()
            return
        # Store the active plotter for interaction handling
        self.active_plotter = chosed_spectrum
        spectrum_plots_created = chosed_spectrum.create_plots()
        spectrum_dataset_info_created = chosed_spectrum.create_dataset_info()

        # Remove previous float panel if it exists
        # if self._float_panel and self._float_panel in self._main_container_layout:
        #     self._main_container_layout.remove(self._float_panel)
        # self._main_container_layout.insert(0, float_panel)
        # self._float_panel = float_panel

        return spectrum_plots_created, spectrum_dataset_info_created

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