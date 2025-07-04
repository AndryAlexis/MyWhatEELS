from .model import Model
import panel as pn
import holoviews as hv
from holoviews import streams
import param
import xarray as xr
import numpy as np
from whateels.components import FileDropper

# Initialize HoloViews with Bokeh backend
hv.extension("bokeh", logo=False)

class View:
    """
    View class for the home page of the WhatEELS application.
    This class is responsible for creating the layout and components of the home page.
    It uses the Model to access constants and configurations.
    """
    def __init__(self, model: Model):
        self.model = model
        self.callbacks = {} # Dictionary to hold callbacks
        
        # Initialize visualization components
        self._init_visualization_components()
        
        # Visualization components (created when dataset is loaded)
        self.reference_image = None
        self.interactive_image = None
        self.spectrum = None
        self.empty_spectrum = None
        self.empty_curve = None
        
        # Interaction streams
        self.tap_stream = None
        self.hover_stream = None
        
        # Click feedback
        self.click_text = param.String(default=model.Constants.CLICK_TEXT_2D_NONE)
        self.click_feedback_widget = None
    
    def _init_visualization_components(self):
        """Initialize the visualization container and placeholder"""
        # Placeholder for when no file is loaded
        self.visualization_placeholder = pn.pane.HTML(
            self.model.Placeholders.NO_FILE_LOADED,
            sizing_mode='stretch_both',  # This makes the placeholder responsive too
            min_height=400
        )
        
        # Container that will hold either placeholder or actual visualization
        self.visualization_container = pn.Column(
            self.visualization_placeholder,
            sizing_mode='stretch_both',  # This makes it fill 100% width and height
        )
    
    def _sidebar_layout(self):
        """
        Create and return the sidebar layout for the view.
        """

        file_dropper = FileDropper(
            valid_extensions=Model.FileDropper.VALID_EXTENSIONS,
            reject_message=Model.FileDropper.REJECT_MESSAGE,
            success_message=Model.FileDropper.SUCCESS_MESSAGE,
            feedback_message=Model.FileDropper.FEEDBACK_MESSAGE,
            on_file_uploaded_callback=self.callbacks.get(Model.Callbacks.FILE_UPLOADED),
            on_file_removed_callback=self.callbacks.get(Model.Callbacks.FILE_REMOVED)
        )
        
        file_dropper_box = pn.WidgetBox(file_dropper)
        
        column = pn.Column(
            file_dropper_box,
            sizing_mode='stretch_width'
        )

        return column
    
    def _main_layout(self):
        """Create and return the main content area with visualization"""
        return self.visualization_container
    
    @property
    def sidebar(self) -> pn.WidgetBox:
        return self._sidebar_layout()
    
    @property
    def main(self):
        return self._main_layout()
    
    @property
    def callbacks(self) -> dict:
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, value : dict):
        if not isinstance(value, dict):
            raise ValueError("Callbacks must be a dictionary")
        self._callbacks = value
    
    def update_visualization(self, visualization_component):
        """
        Update the main area with a new visualization component
        
        Args:
            visualization_component: Panel component to display (from VisualDisplay)
        """
        self.visualization_container.clear()
        self.visualization_container.append(visualization_component)
    
    def reset_visualization(self):
        """Reset the main area to show the placeholder"""
        self.visualization_container.clear()
        self.visualization_container.append(self.visualization_placeholder)
    
    def create_eels_visualization(self, dataset_type: str):
        """
        Create EELS visualization based on dataset type
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
        """
        try:
            if dataset_type == self.model.Constants.SINGLE_SPECTRUM:
                return self._create_single_spectrum_layout()
            elif dataset_type == self.model.Constants.SPECTRUM_LINE:
                return self._create_spectrum_line_layout()
            elif dataset_type == self.model.Constants.SPECTRUM_IMAGE:
                return self._create_spectrum_image_layout()
            else:
                return self.visualization_placeholder
        except Exception as e:
            print(f"Error creating visualization: {e}")
            return self.visualization_placeholder
    
    def _create_single_spectrum_layout(self):
        """Create layout for single spectrum visualization"""
        # Create spectrum plot
        spectrum_data = self.model.dataset.ElectronCount.squeeze()
        
        # Clean spectrum data for any remaining NaN/inf values
        spectrum_data = spectrum_data.fillna(0.0)
        spectrum_data = spectrum_data.where(np.isfinite(spectrum_data), 0.0)
        
        spectrum = hv.Curve(
            spectrum_data,
            kdims=[self.model.Constants.ELOSS],
            vdims=[self.model.Constants.ELECTRON_COUNT]
        ).opts(
            width=800,
            height=400,
            color=self.model.Colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='EELS Spectrum'
        )
        
        # Convert to Panel
        spectrum_pane = pn.pane.HoloViews(spectrum, sizing_mode='stretch_width')
        
        return pn.Column(
            spectrum_pane,
            sizing_mode='stretch_both'
        )
    
    def _create_spectrum_line_layout(self):
        """Create layout for spectrum line visualization"""
        # Sum over y dimension to create image
        image_data = self.model.dataset.ElectronCount.squeeze()
        
        # Clean image data for any remaining NaN/inf values
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        
        # Clean coordinates as well
        x_coords = self.model.dataset.coords[self.model.Constants.AXIS_X]
        eloss_coords = self.model.dataset.coords[self.model.Constants.ELOSS]
        
        # Ensure coordinates are finite
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        eloss_coords = eloss_coords.where(np.isfinite(eloss_coords), 0.0)
        
        # Create clean dataset for the image
        clean_image_data = image_data.assign_coords({
            self.model.Constants.AXIS_X: x_coords,
            self.model.Constants.ELOSS: eloss_coords
        })
        
        # Create image
        image = hv.Image(
            clean_image_data,
            kdims=[self.model.Constants.AXIS_X, self.model.Constants.ELOSS]
        ).opts(
            width=600,
            height=400,
            cmap=self.model.Colors.GREYS_R,
            xlabel='Position',
            ylabel='Energy Loss (eV)',
            title='EELS Spectrum Line',
            invert_yaxis=True,
            tools=['hover', 'tap']
        )
        
        # Create empty spectrum for interaction using dataset's energy axis
        eloss_coords = self.model.dataset.coords[self.model.Constants.ELOSS]
        empty_data = xr.zeros_like(eloss_coords)
        
        # Validate coordinates
        if len(eloss_coords) == 0:
            raise ValueError("Energy loss coordinates are empty")
        
        empty_spectrum = hv.Curve(
            (eloss_coords, empty_data),
            kdims=[self.model.Constants.ELOSS],
            vdims=[self.model.Constants.ELECTRON_COUNT]
        ).opts(
            width=600,
            height=300,
            color=self.model.Colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='Selected Spectrum'
        )
        
        # Setup interaction - use tap instead of hover for spectrum line
        self.tap_stream = streams.Tap(x=0, y=0, source=image)
        self.hover_stream = None  # Keep for compatibility but not used
        
        # Convert to Panel and store reference for dynamic updates
        image_pane = pn.pane.HoloViews(image, sizing_mode='stretch_width')
        self.spectrum_pane = pn.pane.HoloViews(empty_spectrum, sizing_mode='stretch_width')
        
        return pn.Column(
            image_pane,
            self.spectrum_pane,
            sizing_mode='stretch_both'
        )
    
    def _create_spectrum_image_layout(self):
        """Create layout for spectrum image (datacube) visualization"""
        # Create reference image (sum over energy loss)
        image_data = self.model.dataset.ElectronCount.sum(self.model.Constants.ELOSS)
        
        # Clean image data for any remaining NaN/inf values
        image_data = image_data.fillna(0.0)
        image_data = image_data.where(np.isfinite(image_data), 0.0)
        
        # Clean coordinates as well
        x_coords = self.model.dataset.coords[self.model.Constants.AXIS_X]
        y_coords = self.model.dataset.coords[self.model.Constants.AXIS_Y]
        
        # Ensure coordinates are finite
        x_coords = x_coords.where(np.isfinite(x_coords), 0.0)
        y_coords = y_coords.where(np.isfinite(y_coords), 0.0)
        
        # Create clean dataset for the image
        clean_image_data = image_data.assign_coords({
            self.model.Constants.AXIS_X: x_coords,
            self.model.Constants.AXIS_Y: y_coords
        })
        
        # Create interactive heatmap
        image = hv.Image(
            clean_image_data,
            kdims=[self.model.Constants.AXIS_X, self.model.Constants.AXIS_Y]
        ).opts(
            width=500,
            height=500,
            cmap=self.model.Colors.GREYS_R,
            xlabel='X Position',
            ylabel='Y Position',
            title='EELS Image (Sum over Energy)',
            invert_yaxis=True,
            tools=['hover', 'tap']
        )
        
        # Create empty spectrum for interaction using dataset's energy axis
        eloss_coords = self.model.dataset.coords[self.model.Constants.ELOSS]
        empty_data = xr.zeros_like(eloss_coords)
        
        # Validate coordinates
        if len(eloss_coords) == 0:
            raise ValueError("Energy loss coordinates are empty")
        
        empty_spectrum = hv.Curve(
            (eloss_coords, empty_data),
            kdims=[self.model.Constants.ELOSS],
            vdims=[self.model.Constants.ELECTRON_COUNT]
        ).opts(
            width=600,
            height=400,
            color=self.model.Colors.BLACK,
            line_width=2,
            xlabel='Energy Loss (eV)',
            ylabel='Electron Count',
            title='Selected Spectrum'
        )
        
        # Setup interaction - use tap instead of hover for spectrum image
        self.tap_stream = streams.Tap(x=0, y=0, source=image)
        self.hover_stream = None  # Keep for compatibility but not used
        
        # Setup click feedback widget
        self.click_feedback_widget = pn.widgets.StaticText(
            value=self.model.Constants.CLICK_TEXT_2D_NONE,
            name='Click Position'
        )
        
        # Convert to Panel and store reference for dynamic updates
        image_pane = pn.pane.HoloViews(image, sizing_mode='stretch_width')
        self.spectrum_pane = pn.pane.HoloViews(empty_spectrum, sizing_mode='stretch_width')
        
        return pn.Row(
            pn.Column(
                image_pane,
                self.click_feedback_widget,
                sizing_mode='stretch_width'
            ),
            self.spectrum_pane,
            sizing_mode='stretch_both'
        )