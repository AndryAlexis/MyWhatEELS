"""
Spectrum image (datacube) visualization composer.
Se reemplaza HoloViews por Panel + Plotly usando la lógica de si_view.py,
pero manteniendo la lógica de acceso a datos y widgets de SpectrumImageVisualizer.
"""

import panel as pn
import numpy as np
import time
from .abstract_eels_visualizer import AbstractEELSVisualizer
from typing import override, TYPE_CHECKING
from whateels.helpers import HTML_ROOT

import plotly.graph_objs as go

if TYPE_CHECKING:
    from ...model import Model
    from ...controller import Controller

class SpectrumImageVisualizer(AbstractEELSVisualizer):
    """
    Version Plotly / Panel del visualizador de Spectrum Image.
    Mantiene la lógica de datos del visualizador original y reemplaza
    HoloViews por Plotly panes y callbacks (hover / click / select).
    """
    
    _STRETCH_WIDTH = "stretch_width"
    
    _DATASET_INFO_HEADER_CLASS = ["dataset-info-header"]
    _DATASET_INFO_CLASS = ["dataset-info", "animated"]
    _DATASET_INFO_TITLE = "<h5 class=\"dataset-info-title\">Dataset Information</h5>"
    _DATASET_DETAILS_NAME = "Dataset Details"
    _DATASET_DETAILS_WIDTH = 350
    _DATASET_DETAILS_HEIGHT = 250
    _DATASET_DETAILS_POSITION = "center"
    _DATASET_DETAILS_HEADER = "### More Dataset Details"
    _DATASET_DETAILS_PLACEHOLDER = "(Add more details here as needed)"

    def __init__(self, model: "Model", controller: "Controller") -> None:
        self._model = model
        self._controller = controller
        
        # Energy axis (eje de energía)
        self._e_axis = self._model.dataset.coords[self._model.constants.ELOSS].values

        self._spectrum_service = self._controller.spectrum_service

        # Last selected pixel (x,y)
        self._last_selected = {"x": 0, "y": 0}

        # Range state for paneB (to preserve zoom/pan)
        self._current_x_range = None
        self._current_y_range = None
        # None = unknown / leave Plotly default; True/False = explicitly requested autorange
        self._current_x_autorange = None
        self._current_y_autorange = None

        # Selection / hover / fitting state (inspired by si_view.py)
        self._region_pairs = []         # lista de (i,j) seleccionados por lasso/box
        self._last_hover_point = None   # último hover {x,y,curve}
        self._last_hover_ts = None
        self._INACTIVITY_MS = 700
        self._fitting_active = False

        # Widgets / panes placeholders
        self.range_slider = None
        self.fitting_button = None
        self.paneA = None  # Plotly heatmap pane
        self.paneB = None  # Plotly spectrum pane
        self._pc = None    # periodic callback handle

        # Setup widgets, plots and callbacks
        self._setup_widgets()
        self._setup_plots()
        self._setup_callbacks()

    # --- Widget Setup (kept from original, but range_slider reused) ---
    def _setup_widgets(self):
        # Range slider already used by earlier implementation
        self.range_slider = pn.widgets.RangeSlider(
            name="Range",
            start=float(self._e_axis[0]) if len(self._e_axis) > 0 else 0.0,
            end=float(self._e_axis[-1]) if len(self._e_axis) > 0 else 1.0,
            value=(float(self._e_axis[0]), float(self._e_axis[-1])),
            sizing_mode="stretch_width",
        )
        self.range_slider.param.watch(self._on_range_changed, 'value')

        # Fitting toggle button
        self.fitting_button = pn.widgets.Button(name="fitting: OFF", button_type="primary")
        self.fitting_button.on_click(self._on_fitting_clicked)
        self.range_slider.visible = False

    # --- Plot / Pane Setup (Plotly) ---
    def _setup_plots(self):
        # Build image (m_image) from data cube in the canonical way used in this class
        # ElectronCount dims assumed (y, x, E)
        da = self._model.dataset.ElectronCount
        # create clean 2D integrated image
        m_image_da = da.sum(self._model.constants.ELOSS)
        m_image = np.asarray(m_image_da.fillna(0.0).where(np.isfinite(m_image_da), 0.0))
        if m_image.ndim != 2:
            raise ValueError(f"Se esperaba imagen 2D integrada, recibido shape={m_image.shape}")

        ny, nx = m_image.shape
        # energy axis
        try:
            energy = np.asarray(self._e_axis)
            if energy.shape[0] != da.shape[-1]:
                energy = np.arange(da.shape[-1])
        except Exception:
            energy = np.arange(da.shape[-1])
        self._energy = energy

        # Build Plotly heatmap (figA) and selectors scatter for box/lasso selections
        heat = go.Heatmap(
            z=m_image,
            x=np.arange(nx),
            y=np.arange(ny),
            colorscale="Greys_r",
            showscale=False,
            name="m_image",
            hovertemplate="i=%{y}, j=%{x}<br>I=%{z}<extra></extra>",
        )

        XX, YY = np.meshgrid(np.arange(nx), np.arange(ny))
        selectors = go.Scattergl(
            x=XX.ravel(),
            y=YY.ravel(),
            mode="markers",
            name="selectors",
            marker=dict(size=6, opacity=0.01),
            hoverinfo="skip",
            selected=dict(marker=dict(opacity=0.3, size=8)),
            unselected=dict(marker=dict(opacity=0.01)),
        )

        figA = go.Figure(data=[heat, selectors])
        figA.update_layout(
            title="m_image (hover) + lasso/box para sumar",
            height=400,
            margin=dict(l=16, r=16, t=50, b=20),
            dragmode="lasso",
        )
        figA.update_yaxes(autorange="reversed", scaleanchor=None, constrain="domain")

        # Pane A (heatmap)
        self.paneA = pn.pane.Plotly(self._to_plotly(figA), config={"responsive": True})

        # Pane B initial message (apply stored ranges if any)
        self.paneB = pn.pane.Plotly(self._set_ranges_and_convert(self._figB_message("figura_B", "mueve el ratón o selecciona")),
                                    height=420, sizing_mode="fixed")

        # Keep references to dataset for spectra lookup
        self._da = da  # xarray DataArray

    # --- Callbacks setup (connect pane watchers & periodic callback) ---
    def _setup_callbacks(self):
        # Attach panel watchers to figA and paneB
        self.paneA.param.watch(self._on_paneA_hover, "hover_data")
        self.paneA.param.watch(self._on_paneA_click, "click_data")
        self.paneA.param.watch(self._on_paneA_selected, "selected_data")

        # relayout_data is emitted by pn.pane.Plotly on axis changes
        self.paneB.param.watch(self._on_paneB_relayout, "relayout_data")

        # Periodic callback for inactivity logic (stopped by default)
        self._pc = pn.state.add_periodic_callback(self._check_inactivity, period=250, start=False)

    # --- Helpers / utilities (from si_view.py adapted) ---
    def _to_plotly(self, obj):
        """Convert go.Figure to dict to avoid Panel<->Plotly relayout issues."""
        try:
            if isinstance(obj, go.Figure):
                return obj.to_plotly_json()
        except Exception:
            pass
        try:
            if isinstance(obj, dict):
                # ensure layout.height exists for consistent rendering
                if "layout" in obj and "height" not in obj["layout"]:
                    obj["layout"]["height"] = 420
                return obj
        except Exception:
            pass
        return obj

    def _figB_message(self, title, subtitle):
        fig = go.Figure()
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(title=title, height=420, margin=dict(l=16, r=16, t=48, b=16))
        fig.add_annotation(
            x=0.5, y=0.6, xref="paper", yref="paper",
            text=subtitle, showarrow=False,
            font=dict(size=22), align="center",
        )
        return fig

    def _figB_hover(self, point):
        if not point:
            return self._figB_message("figura_B_hover", "hover sobre un píxel…")
        i, j = int(point["y"]), int(point["x"])
        spec = self._spectrum_service.spectrum_from_pixel(i, j)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self._energy, y=spec, mode="lines", name=f"(i={i}, j={j})"))
        fig.update_layout(title="figura_B_hover", height=420, margin=dict(l=16, r=16, t=48, b=16),
                          xaxis_title="Energía", yaxis_title="Intensidad")
        return fig

    def _figB_region(self, pairs):
        res = self._spectrum_service.spectrum_from_indices(pairs)
        if res is None:
            return self._figB_message("figura_B_region", "selecciona con lasso/box…")
        spec, N = res
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self._energy, y=spec, mode="lines", name=f"suma (N={N})"))
        fig.update_layout(title=f"figura_B_region — suma (N={N})", height=420,
                          margin=dict(l=16, r=16, t=48, b=16), xaxis_title="Energía", yaxis_title="Intensidad")
        return fig

    # --- Inactivity logic (restaurar selección tras inactivity) ---
    def _now_ms(self):
        return int(time.time() * 1000)

    def _check_inactivity(self):
        # No selection -> nothing to do
        if not self._region_pairs:
            if self._pc.running:
                self._pc.stop()
            return

        # If there is no hover timestamp, ensure selection is shown and timer stopped
        if self._last_hover_ts is None:
            if self._pc.running:
                self._pc.stop()
            fig = self._figB_region(self._region_pairs)
            if self._fitting_active:
                res = self._spectrum_service.spectrum_from_indices(self._region_pairs)
                if res is not None:
                    spec, _N = res
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            return

        if self._now_ms() - int(self._last_hover_ts) >= self._INACTIVITY_MS:
            fig = self._figB_region(self._region_pairs)
            if self._fitting_active:
                res = self._spectrum_service.spectrum_from_indices(self._region_pairs)
                if res is not None:
                    spec, _N = res
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            if self._pc.running:
                self._pc.stop()

    # --- Pane A event handlers (hover / click / selected) ---
    def _on_paneA_hover(self, event):
        point = self._controller.region_service.extract_point(event.new)
        if point is None:
            return
        self._last_hover_point = point
        if self._region_pairs:
            # Temporary hover while a selection exists: show hover spectrum and start/renew timer
            fig = self._figB_hover(self._last_hover_point)
            if self._fitting_active:
                i, j = int(point["y"]), int(point["x"])
                spec = self._spectrum_service.spectrum_from_pixel(i, j)
                if spec is not None:
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            self._last_hover_ts = self._now_ms()
            if not self._pc.running:
                self._pc.start()
        else:
            # No selection: persistent hover view, no inactivity timer
            fig = self._figB_hover(self._last_hover_point)
            if self._fitting_active:
                i, j = int(point["y"]), int(point["x"])
                spec = self._spectrum_service.spectrum_from_pixel(i, j)
                if spec is not None:
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            if self._pc.running:
                self._pc.stop()
            self._last_hover_ts = None

    def _on_paneA_click(self, event):
        point = self._controller.region_service.extract_point(event.new)
        if point is None:
            return
        self._last_hover_point = point
        fig = self._figB_hover(self._last_hover_point)
        if self._fitting_active:
            i, j = int(point["y"]), int(point["x"])
            spec = self._spectrum_service.spectrum_from_pixel(i, j)
            if spec is not None:
                fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
        self.paneB.object = self._set_ranges_and_convert(fig)
        if self._region_pairs:
            self._last_hover_ts = self._now_ms()
            if not self._pc.running:
                self._pc.start()
        else:
            if self._pc.running:
                self._pc.stop()
            self._last_hover_ts = None

    def _on_paneA_selected(self, event):
        pairs = self._controller.region_service.extract_region(event.new)
        self._region_pairs = pairs
        if not pairs:
            if self._pc.running:
                self._pc.stop()
            self._last_hover_ts = None
            if self._last_hover_point is not None:
                fig = self._figB_hover(self._last_hover_point)
                if self._fitting_active:
                    i, j = int(self._last_hover_point["y"]), int(self._last_hover_point["x"])
                    spec = self._spectrum_service.spectrum_from_pixel(i, j)
                    if spec is not None:
                        fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
                self.paneB.object = self._set_ranges_and_convert(fig)
            else:
                self.paneB.object = self._set_ranges_and_convert(self._figB_message("figura_B", "mueve el ratón o selecciona"))
            return

        fig = self._figB_region(self._region_pairs)
        if self._fitting_active:
            res = self._spectrum_service.spectrum_from_indices(self._region_pairs)
            if res is not None:
                spec, N = res
                fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
        self.paneB.object = self._set_ranges_and_convert(fig)

        # prepare inactivity behaviour: stop periodic callback until next hover
        if self._pc.running:
            self._pc.stop()
        self._last_hover_ts = None

    # --- Pane B relayout (preserve zoom/pan ranges) ---
    def _on_paneB_relayout(self, event):
        # Robustly extract ranges/autorange from relayout payloads emitted by Plotly
        try:
            data = event.new or {}

            # X axis: support 'xaxis.range', 'xaxis.range[0/1]', 'xaxis.autorange'
            if 'xaxis.range[0]' in data and 'xaxis.range[1]' in data:
                self._current_x_range = (float(data['xaxis.range[0]']), float(data['xaxis.range[1]']))
                self._current_x_autorange = False
            elif 'xaxis.range' in data:
                rng = data.get('xaxis.range')
                if isinstance(rng, (list, tuple)) and len(rng) == 2:
                    self._current_x_range = (float(rng[0]), float(rng[1]))
                    self._current_x_autorange = False
            elif 'xaxis.autorange' in data:
                # autorange True means clear explicit range
                self._current_x_autorange = bool(data.get('xaxis.autorange'))
                if self._current_x_autorange:
                    self._current_x_range = None

            # Y axis: same logic
            if 'yaxis.range[0]' in data and 'yaxis.range[1]' in data:
                self._current_y_range = (float(data['yaxis.range[0]']), float(data['yaxis.range[1]']))
                self._current_y_autorange = False
            elif 'yaxis.range' in data:
                rng = data.get('yaxis.range')
                if isinstance(rng, (list, tuple)) and len(rng) == 2:
                    self._current_y_range = (float(rng[0]), float(rng[1]))
                    self._current_y_autorange = False
            elif 'yaxis.autorange' in data:
                self._current_y_autorange = bool(data.get('yaxis.autorange'))
                if self._current_y_autorange:
                    self._current_y_range = None

            # Some Plotly versions emit nested keys or different payload shapes; handled permissively above.
        except Exception:
            # Ignore noisy relayout payloads
            pass

    def _apply_current_ranges(self, fig):
        """Apply stored ranges to fig if present."""
        try:
            # Only set explicit ranges when available. Only set autorange when explicitly known.
            if self._current_x_range is not None:
                fig.update_xaxes(range=self._current_x_range)
            elif self._current_x_autorange is not None:
                fig.update_xaxes(autorange=bool(self._current_x_autorange))
            if self._current_y_range is not None:
                fig.update_yaxes(range=self._current_y_range)
            elif self._current_y_autorange is not None:
                fig.update_yaxes(autorange=bool(self._current_y_autorange))
        except Exception:
            pass
        return fig

    def _set_ranges_and_convert(self, fig):
        # Ensure we operate on a go.Figure to apply ranges reliably
        try:
            fig_obj = fig if isinstance(fig, go.Figure) else go.Figure(fig)
        except Exception:
            # fallback: empty figure
            fig_obj = go.Figure()
        self._apply_current_ranges(fig_obj)
        return self._to_plotly(fig_obj)

    # --- Fitting and range behaviour ---
    def _on_fitting_clicked(self, event):
        self._fitting_active = not self._fitting_active
        self.fitting_button.name = f"fitting: {'ON' if self._fitting_active else 'OFF'}"
        self.fitting_button.button_type = "danger" if self._fitting_active else "primary"
        self.range_slider.visible = self._fitting_active

        # Refresh current view
        if self._region_pairs:
            fig = self._figB_region(self._region_pairs)
            if self._fitting_active:
                res = self._spectrum_service.spectrum_from_indices(self._region_pairs)
                if res is not None:
                    spec, _ = res
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            return

        if self._last_hover_point is not None:
            fig = self._figB_hover(self._last_hover_point)
            if self._fitting_active:
                i, j = int(self._last_hover_point["y"]), int(self._last_hover_point["x"])
                spec = self._spectrum_service.spectrum_from_pixel(i, j)
                if spec is not None:
                    fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            return

        self.paneB.object = self._set_ranges_and_convert(self._figB_message("Fitting", "Modo fitting: " + ("activado" if self._fitting_active else "desactivado")))

    def _on_range_changed(self, event):
        """Refresh paneB when the fit range slider changes (only when fitting is active)."""
        if not self._fitting_active:
            return
        if self._region_pairs:
            fig = self._figB_region(self._region_pairs)
            res = self._spectrum_service.spectrum_from_indices(self._region_pairs)
            if res is not None:
                spec, _ = res
                fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)
            return
        if self._last_hover_point is not None:
            fig = self._figB_hover(self._last_hover_point)
            i, j = int(self._last_hover_point["y"]), int(self._last_hover_point["x"])
            spec = self._spectrum_service.spectrum_from_pixel(i, j)
            if spec is not None:
                fig = self._controller.fitting_service.add_fit_traces(fig, self._energy, spec, range_values=self.range_slider.value)
            self.paneB.object = self._set_ranges_and_convert(fig)

    # --- Public layout builders (used by controller) ---
    @override
    def create_plots(self):
        right_col = pn.Column(self.paneB, self.fitting_button, self.range_slider, sizing_mode="stretch_width")
        app = pn.Column(
            pn.Row(self.paneA, right_col, sizing_mode="stretch_width"),
            sizing_mode="stretch_width",
        )
        return app

    @override
    def create_dataset_info(self):
        attrs = self._model.dataset.attrs if self._model.dataset is not None else {}
        shape = attrs.get('shape', 'N/A')
        beam_energy = attrs.get('beam_energy', 'N/A')
        convergence_angle = attrs.get('convergence_angle', 'N/A')
        collection_angle = attrs.get('collection_angle', 'N/A')

        # Load metadata button HTML
        metadata_html_path = HTML_ROOT / "metadata_info.html"
        with open(metadata_html_path, 'r', encoding='utf-8') as f:
            metadata_button_html = f.read()
        
        metadata_button = pn.pane.HTML(metadata_button_html, margin=0)

        # Main info panel
        header = pn.Row(
            pn.pane.HTML(self._DATASET_INFO_TITLE, sizing_mode=self._STRETCH_WIDTH, margin=0),
            metadata_button,
            sizing_mode=self._STRETCH_WIDTH,
            css_classes=self._DATASET_INFO_HEADER_CLASS,
            margin=0
        )

        dataset_info = pn.Column(
            header,
            pn.Spacer(height=5),
            pn.Row(
                pn.Row(
                    pn.pane.HTML("<strong>Shape:</strong>"),
                    sizing_mode=self._STRETCH_WIDTH
                ),
                pn.pane.Str(shape),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.Row(
                    pn.pane.HTML("<strong>Beam Energy:</strong>"),
                    sizing_mode=self._STRETCH_WIDTH
                ),
                pn.pane.Str(f"{beam_energy} keV"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.Row(
                    pn.pane.HTML("<strong>Convergence Angle:</strong>"),
                    sizing_mode=self._STRETCH_WIDTH
                ),
                pn.pane.Str(f"{convergence_angle} mrad"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Row(
                pn.Row(
                    pn.pane.HTML("<strong>Collection Angle:</strong>"),
                    sizing_mode=self._STRETCH_WIDTH
                ),
                pn.pane.Str(f"{collection_angle} mrad"),
                sizing_mode=self._STRETCH_WIDTH
            ),
            pn.Spacer(height=10),
            sizing_mode=self._STRETCH_WIDTH,
            css_classes=self._DATASET_INFO_CLASS
        )
        return dataset_info
