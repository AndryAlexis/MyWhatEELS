import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objs as go

class SpectrumFittingService:
    """
    Service for fitting and background subtraction of EELS spectra.
    """
    @staticmethod
    def powerlaw(x, A, k):
        with np.errstate(divide='ignore', invalid='ignore'):
            return A * np.power(x, k)

    @staticmethod
    def add_fit_traces(fig, x, y, range_values=None):
        """
        Add powerlaw fit and subtraction traces to fig (non-destructive).
        """
        try:
            mask = np.isfinite(x) & np.isfinite(y) & (y > 0) & (x > 0)
            if range_values is not None:
                mask &= (x >= range_values[0]) & (x <= range_values[1])
            x_f = x[mask]
            y_f = y[mask]
            if x_f.size < 3:
                return fig
            params, _ = curve_fit(SpectrumFittingService.powerlaw, x_f, y_f, maxfev=10000)
            y_fit = SpectrumFittingService.powerlaw(x, *params)
            newfig = go.Figure(fig)
            newfig.add_trace(go.Scatter(x=x, y=y_fit, line=dict(color='crimson'), name='PowerLaw Fit'))
            newfig.add_trace(
                go.Scatter(
                    x=x,
                    y=(y - y_fit),
                    fill='tozeroy',
                    line=dict(color='rgba(255,160,122,0.2)'),
                    fillcolor='rgba(255,160,122,0.6)',
                    name='Background Subtraction',
                )
            )
            newfig.update_layout(
                legend=dict(
                    x=0.98,
                    y=0.98,
                    xanchor='right',
                    yanchor='top',
                    bgcolor='rgba(255,255,255,0.6)',
                    bordercolor='rgba(0,0,0,0.1)',
                    borderwidth=1,
                )
            )
            return newfig
        except Exception:
            return fig
