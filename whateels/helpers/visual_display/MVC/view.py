"""
View layer for EELS visualization - handles all UI components creation and styling.
"""

import holoviews as hv
from holoviews import streams
import panel as pn
import param
from typing import Tuple, Optional

from .model import *

hv.extension("bokeh", logo=False)


class View:
    """Handles creation of all visual components for EELS data visualization."""
    
    def __init__(self, model: Model):
        """
        Initialize the view with a model.
        
        Args:
            model: Model object containing data and configuration
        """
        self.model = model
        self.click_feedback_widget: Optional[pn.Param] = None
        
        # Visual components (will be created by specific methods)
        self.reference_image: Optional[hv.Image] = None
        self.interactive_image: Optional[hv.HeatMap] = None
        self.line_image: Optional[hv.Image] = None
        self.spectrum: Optional[hv.Area] = None
        self.empty_spectrum: Optional[hv.Area] = None
        self.empty_curve: Optional[hv.Curve] = None
        
        # Interaction streams
        self.tap_stream: Optional[streams.Tap] = None
        self.hover_stream: Optional[streams.PointerXY] = None
        
    def setup_click_feedback_widget(self, param_obj: param.Parameterized) -> pn.Param:
        """Setup the widget for displaying click feedback messages."""
        self.click_feedback_widget = pn.Param(
            param_obj.param[Constants.CLICK_TEXT],
            widgets={Constants.CLICK_TEXT: pn.widgets.StaticText},
            parameters=[Constants.CLICK_TEXT],
            show_labels=False,
            show_name=False
        )
        return self.click_feedback_widget
    
    def create_spectrum_image_components(self) -> None:
        """Create all visual components for spectrum image (3D datacube) visualization."""
        # Reference image for coordinate mapping
        self.reference_image = hv.Image(
            self.state.dataset.ElectronCount.sum(Constants.ELOSS),
            kdims=UIConfig.KDIMS_XY
        ).opts(
            cmap=Colors.GREYS_R,
            invert_yaxis=True,
            xaxis=None,
            yaxis=None,
            xlim=self.state.x_limits,
            ylim=self.state.y_limits
        )
        
        # Interactive heatmap for spectrum image
        self.interactive_image = hv.HeatMap(
            self.model.dataset.ElectronCount.sum(Constants.ELOSS),
            kdims=UIConfig.KDIMS_XY
        ).opts(
            cmap=Colors.GREYS_R,
            invert_yaxis=True,
            xaxis=None,
            yaxis=None,
            xlim=self.model.x_limits,
            ylim=self.model.y_limits,
            line_width=1.5,
            fill_alpha=0.5,
            line_alpha=0.1,
            bgcolor=Colors.DARKGREY,
            hover_line_color=Colors.LIMEGREEN,
            hover_line_alpha=1,
            hover_fill_alpha=1,
            selection_line_alpha=1,
            selection_line_color=Colors.RED,
            selection_fill_alpha=1,
            nonselection_line_alpha=0.1,
            nonselection_line_color=Colors.WHITE,
            nonselection_fill_alpha=0.5,
            tools=UIConfig.HOVER_TAP_TOOLS
        )
        
        # Create empty placeholders
        self._create_empty_spectrum_components(frame_width=600, frame_height=300)
        
        # Setup interaction streams
        self.tap_stream = streams.Tap(x=-1, y=-1, source=self.interactive_image)
        self.hover_stream = streams.PointerXY(x=-1, y=-1, source=self.interactive_image)
    
    def create_spectrum_line_components(self) -> None:
        """Create all visual components for spectrum line (2D line scan) visualization."""
        # Main image display for line scan
        self.line_image = hv.Image(
            self.model.dataset.ElectronCount, 
            kdims=UIConfig.KDIMS_Y_ELOSS
        ).opts(
            cmap=Colors.GREYS_R,
            invert_axes=True,
            invert_yaxis=True,
            frame_width=900,
            frame_height=125,
            yformatter=Formatters.INTEGER,
            xaxis=None,
            toolbar=None,
            bgcolor=Colors.GHOSTWHITE
        )
        
        # Create empty placeholders
        self._create_empty_spectrum_components(frame_width=900, frame_height=250)
        
        # Setup interaction streams
        self.tap_stream = streams.Tap(x=-1, y=-1, source=self.line_image)
        self.hover_stream = streams.PointerXY(x=-1, y=-1, source=self.line_image)
    
    def create_single_spectrum_component(self) -> None:
        """Create visual component for single spectrum visualization."""
        self.spectrum = hv.Area(self.model.dataset.ElectronCount.isel(x=0, y=0)).opts(
            color=Colors.LIMEGREEN,
            fill_alpha=0.5,
            line_color=Colors.BLACK,
            frame_width=900,
            frame_height=350,
            yformatter=Formatters.SCIENTIFIC,
            framewise=True,
            shared_axes=False,
            show_grid=True
        )
    
    def _create_empty_spectrum_components(self, frame_width: int, frame_height: int) -> None:
        """Create empty spectrum and curve components with specified dimensions."""
        # Empty spectrum placeholder
        self.empty_spectrum = hv.Area(self.model.empty_curve_dataset).opts(
            frame_height=frame_height,
            yformatter=Formatters.SCIENTIFIC,
            frame_width=frame_width,
            shared_axes=False,
            framewise=True,
            show_grid=True,
            color=Colors.GREY,
            fill_alpha=0.75,
            line_width=0
        )
        
        # Empty curve for fallback display
        self.empty_curve = hv.Curve(self.model.empty_curve_dataset).opts(
            frame_height=frame_height,
            yformatter=Formatters.SCIENTIFIC,
            frame_width=frame_width,
            shared_axes=False,
            framewise=True,
            show_grid=True,
            color=Colors.BLACK,
            line_width=2.0
        )
    
    def create_dynamic_spectrum_maps(self, hover_callback, tap_callback) -> Tuple[hv.DynamicMap, hv.DynamicMap]:
        """Create dynamic maps for hover and tap interactions."""
        if self.model.dataset_type == Constants.SPECTRUM_IMAGE:
            frame_width, frame_height = 600, 300
        else:  # SPECTRUM_LINE
            frame_width, frame_height = 900, 250
            
        spectrum_hover = hv.DynamicMap(
            hover_callback, 
            streams=[self.hover_stream]
        ).opts(
            frame_height=frame_height,
            yformatter=Formatters.SCIENTIFIC,
            frame_width=frame_width,
            shared_axes=False,
            framewise=True,
            show_grid=True
        )
        
        spectrum_tap = hv.DynamicMap(
            tap_callback,
            streams=[self.tap_stream]
        ).opts(
            frame_height=frame_height,
            yformatter=Formatters.SCIENTIFIC,
            frame_width=frame_width,
            shared_axes=False,
            framewise=True,
            show_grid=True
        )
        
        return spectrum_hover, spectrum_tap
    
    def create_spectrum_visualization(self, x: float, y: float, is_tap: bool = False) -> hv.Element:
        """Create a spectrum visualization for the given coordinates."""
        if not self.model.is_point_in_bounds(x, y):
            # TODO - look if this is still needed
            # return self.empty_spectrum if self.model.dataset_type != Constants.SPECTRUM_LINE or is_tap else self.empty_spectrum
            return self.empty_spectrum
        
        if self.model.dataset_type == Constants.SPECTRUM_IMAGE:
            closest_x, closest_y = self.reference_image.closest((x, y))
            spectrum_data = self.model.dataset.isel(x=int(closest_x), y=int(closest_y))
            
            if is_tap:
                # Tap visualization - highlighted spectrum
                spectrum = hv.Area(spectrum_data).opts(
                    fill_color=Colors.ORANGERED,
                    fill_alpha=0.5,
                    line_color=Colors.DARKRED,
                    line_width=1.5,
                    line_alpha=1
                )
            else:
                # Hover visualization - preview spectrum
                spectrum = hv.Area(spectrum_data).opts(
                    fill_color=Colors.LIMEGREEN,
                    fill_alpha=0.5,
                    line_width=0
                )
                
        elif self.model.dataset_type == Constants.SPECTRUM_LINE:
            closest_y = self.line_image.closest((x, y))[1]
            spectrum_data = self.model.dataset.isel(y=int(closest_y), x=0)
            
            if is_tap:
                # Tap visualization - curve spectrum
                spectrum = hv.Curve(spectrum_data).opts(
                    color=Colors.MIDNIGHTBLUE,
                    line_width=2.0
                )
            else:
                # Hover visualization - area spectrum
                spectrum = hv.Area(spectrum_data).opts(
                    color=Colors.GREY,
                    fill_alpha=0.75,
                    line_width=0
                )
        
        spectrum.relabel(UIConfig.TICK_FORMATTERS_LABEL)
        return spectrum
    
    def create_panel_layout(self, dataset_type: str, click_widget: pn.Param):
        """Create the panel layout for the visualization."""
        click_widget[0].margin = (0, 10, 5, 10)
        
        # Create static text widgets for labels
        dataset_label = pn.widgets.StaticText(value=UIConfig.DATASET_DISPLAY_LABEL)
        selected_data_label = pn.widgets.StaticText(value=UIConfig.SELECTED_DATA_LABEL)
        dataset_name_widget = pn.widgets.StaticText(value=self.model.get_dataset_name())
        
        # Create panel layouts based on dataset type
        if dataset_type == Constants.SINGLE_SPECTRUM:
            header_row = pn.Row(dataset_label, dataset_name_widget, width=1000)
            return pn.Column(header_row, self.spectrum, width=1000, height=550)
            
        elif dataset_type == Constants.SPECTRUM_IMAGE:
            header_info = pn.Column(
                pn.Row(dataset_label, dataset_name_widget),
                pn.Row(selected_data_label, click_widget),
                width=1000
            )
            
            # These will be set by the controller
            spectrum_hover = getattr(self, Constants.SPECTRUM_HOVER_ATTR, pn.Spacer())
            spectrum_tap = getattr(self, Constants.SPECTRUM_TAP_ATTR, pn.Spacer())
            
            return pn.Column(
                header_info,
                pn.Row(
                    self.interactive_image,
                    spectrum_hover * spectrum_tap,
                    width=1000,
                    height=450
                ),
                width=1000,
                height=550
            )
            
        elif dataset_type == Constants.SPECTRUM_LINE:
            header_info = pn.Column(
                pn.Row(dataset_label, dataset_name_widget),
                pn.Row(selected_data_label, click_widget),
                width=1000
            )
            
            # These will be set by the controller
            spectrum_hover = getattr(self, Constants.SPECTRUM_HOVER_ATTR, pn.Spacer())
            spectrum_tap = getattr(self, Constants.SPECTRUM_TAP_ATTR, pn.Spacer())
            
            return pn.Column(
                header_info,
                self.line_image,
                spectrum_hover * spectrum_tap,
                width=1000,
                height=550
            )
        else:
            # Fallback for unknown dataset types
            return pn.Spacer(width=1000, height=550, background=Colors.GAINSBORO)
