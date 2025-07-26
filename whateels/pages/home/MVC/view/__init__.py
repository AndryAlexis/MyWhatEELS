from ..model import Model
from .eels_plot_factory import EELSPlotFactory
import panel as pn
import holoviews as hv
from whateels.components import FileDropper

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

    def __init__(self, model: Model):
        # Callbacks dictionary to hold event handlers
        self.callbacks = {}
        # Placeholder for dataset attributes info in sidebar (widgets will be placed here)
        self._dataset_info_pane = pn.Column(sizing_mode=self._STRETCH_WIDTH)
        self.model = model

        # Factory for creating EELS plots
        self.eels_plot_factory = EELSPlotFactory(model, self)
        
        # Main layout that will switch between UI states
        self._main_container_layout = None
        
        # Placeholders for _main_container_layout states
        self._loading_placeholder = None
        self._no_file_placeholder = None
        self._error_placeholder = None

        # Active plotter (to access interaction streams)
        self.active_plotter = None
        
        # Initialize UI components
        self._init_visualization_components()

    @property
    def sidebar(self) -> pn.Column:
        return self._sidebar_layout()
    
    @property
    def main(self) -> pn.Column:
        return self._main_layout()
    
    @property
    def callbacks(self) -> dict:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("Callbacks must be a dictionary")
        self._callbacks = value
        
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
    
    def _sidebar_layout(self):
        """Create and return the sidebar layout"""
        file_dropper = FileDropper(
            valid_extensions=self.model.file_dropper.VALID_EXTENSIONS,
            reject_message=self.model.file_dropper.REJECT_MESSAGE,
            success_message=self.model.file_dropper.SUCCESS_MESSAGE,
            feedback_message=self.model.file_dropper.FEEDBACK_MESSAGE,
            on_file_uploaded_callback=self.callbacks.get(self.model.callbacks.FILE_UPLOADED),
            on_file_removed_callback=self.callbacks.get(self.model.callbacks.FILE_REMOVED)
        )
        
        return pn.Accordion(
            ("File Dropper", file_dropper),  # File dropper component
            #self._dataset_info_pane,  # Información de datos debajo del file_dropper
            sizing_mode=self._STRETCH_WIDTH,
            active=[0],  # Start with file dropper open
            toggle=True
        )

    def add_sidebar_component(self, panel_tuple: tuple):
        """
        Add a new panel to the sidebar Accordion.
        panel_tuple: tuple of (str, pn.Widget)
        """
        if not (isinstance(panel_tuple, tuple) and len(panel_tuple) == 2):
            raise ValueError("Argument must be a tuple: (title: str, component: pn.Widget)")
        title, component = panel_tuple
        if not isinstance(title, str):
            raise ValueError("First element must be a string (panel title)")
        if not isinstance(component, pn.Widget):
            raise ValueError("Second element must be a Panel Widget")
        self._sidebar_layout().append(panel_tuple)
        
    def remove_sidebar_component_by_title(self, title: str):
        """
        Remove the first sidebar panel with the given title from the Accordion.
        """
        sidebar = self._sidebar_layout()
        # Find the first index with matching title
        for i, (panel_title, _) in enumerate(sidebar):
            if panel_title == title:
                sidebar.pop(i)
                return
        raise ValueError(f"No sidebar panel found with title: {title}")
    
    def _main_layout(self):
        """Create and return the main content area"""
    
        self._main_container_layout = pn.Column(
            self._no_file_placeholder,
            sizing_mode=self._STRETCH_BOTH
        )
        return self._main_container_layout

    def update_main_layout(self, plot_component):
        """Update the main area with a new plot component"""
        self._main_container_layout.clear()
        self._main_container_layout.append(plot_component)
    
    def show_loading(self):
        """Show loading screen while processing file"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._loading_placeholder)
    
    def reset_main_layout(self):
        """Reset the main area to show the placeholder"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._no_file_placeholder)
        
    def show_error(self):
        """Show error placeholder when an error occurs"""
        self._main_container_layout.clear()
        self._main_container_layout.append(self._error_placeholder)
    
    def create_eels_plot(self, dataset_type: str):
        """
        Create EELS plots based on dataset type.
        
        Args:
            dataset_type: Type of dataset (SSp, SLi, or SIm)
            
        Returns:
            Panel component with the appropriate plot visualization, or None
            if an error occurred (in which case the view will already show an error)
        """
        plot_result = self.eels_plot_factory.create_plots(dataset_type)

        if plot_result is None:
            return None

        self.active_plotter = self.eels_plot_factory.current_spectrum_visualizer_renderer

        try:
            self._dataset_info_pane.clear()
            attrs = self.model.dataset.attrs if self.model.dataset else {}
            image_name = attrs.get('image_name', '')
            shape = attrs.get('shape', [])
            shape = [shape[1], shape[0], shape[2]] if len(shape) == 3 else shape
            e0 = attrs.get('beam_energy', 0)
            alpha = attrs.get('convergence_angle', 0)
            beta = attrs.get('collection_angle', 0)

            # Estilo común para todos los widgets
            widget_style = {
                "font-size": "11px",
                "height": "24px",
                "margin": "0px",
                "padding": "0px 5px",
                "line-height": "24px",
                "box-sizing": "border-box"
            }

            # Widgets interactivos con estilo unificado
            literal_e0 = pn.widgets.LiteralInput(
                name='', value=e0, type=float, 
                styles=widget_style, width=120
            )
            literal_alpha = pn.widgets.LiteralInput(
                name='', value=alpha, type=float,
                styles=widget_style, width=120
            )
            literal_beta = pn.widgets.LiteralInput(
                name='', value=beta, type=float,
                styles=widget_style, width=120
            )

            # Botón con ajustes especiales para alineación
            more_button = pn.widgets.Button(
                name="more ...",
                button_type="default",
                styles={
                    **widget_style,
                    "padding": "0px",  # Padding reducido para botones
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center"
                },
                width=120,
                height=24
            )

            # Texto de shape con contenedor ajustado
            shape_str = pn.pane.Str(
                str(shape),
                styles={
                    "font-size": "11px",
                    "margin": "0px",
                    "height": "24px",
                    "line-height": "24px",
                    "padding": "3px 5px"  # Compensa diferencias de alineación
                },
                width=120
            )

            # Estilo para etiquetas Markdown
            md_style = {
                "font-size": "11px",
                "margin": "0px",
                "height": "24px",
                "line-height": "24px",
                "padding": "3px 0px"  # Compensación vertical
            }

            # Etiquetas con estilo consistente
            md_labels = [
                pn.pane.Markdown("**Image Info**", styles=md_style, width=140),
                pn.pane.Markdown("**Shape:**", styles=md_style, width=140),
                pn.pane.Markdown("**Beam Energy:**", styles=md_style, width=140),
                pn.pane.Markdown("**Convergence Angle:**", styles=md_style, width=140),
                pn.pane.Markdown("**Collection Angle:**", styles=md_style, width=140),
            ]

            # Valores correspondientes (misma orden que las etiquetas)
            values = [
                more_button,
                shape_str,
                literal_e0,
                literal_alpha,
                literal_beta
            ]

            # Crear la tabla con GridBox ajustado
            table_grid = pn.GridBox(
                *(item for pair in zip(md_labels, values) for item in pair),
                ncols=2,
                sizing_mode="stretch_width",
                styles={
                    "grid-row-gap": "0px",  # Eliminar espacio entre filas
                    "align-items": "center"  # Alineación vertical centrada
                }
            )

            # Añadir la tabla al sidebar
            self._dataset_info_pane.append(table_grid)
            # Crear FloatPanel con la misma tabla, inicialmente oculto
            # Crear FloatPanel con la misma tabla, inicialmente oculto (usar 'name' en lugar de 'title')
            float_panel = pn.layout.FloatPanel(
                table_grid, name='Metadata Details', width=350, height=200, visible=False
            )
            self._dataset_info_pane.append(float_panel)
            # Mostrar FloatPanel al hacer click en more_button
            more_button.on_click(lambda event: setattr(float_panel, 'visible', True))

        except Exception as e:
            print(f"Error al crear la interfaz: {str(e)}")
            pass

        return plot_result

    
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