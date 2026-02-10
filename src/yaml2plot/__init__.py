"""
yaml2plot - SPICE Waveform Visualization Package

A Python package for visualizing SPICE simulation waveforms, designed primarily
for Jupyter notebook integration with both simple plotting functions and advanced
signal processing capabilities.
"""

__version__ = "2.0.1"
__author__ = "Jianxun Zhu"

# Core classes
from .core.plotspec import PlotSpec
from .core.wavedataset import WaveDataset

# Main API functions
from .core.plotting import plot
from .loader import (
    load_csv_data,
    load_csv_data_batch,
    load_spice_raw,
    load_spice_raw_batch,
)

# Renderer helpers
from .utils.env import configure_plotly_renderer

# Plotly imports for user access
import plotly.io as pio


def set_renderer(renderer: str = "auto"):
    """
    Set the Plotly renderer for yaml2plot plots.

    Args:
        renderer: Renderer type - "auto", "browser", "notebook", "plotly_mimetype", etc.
                 "auto" (default) detects environment automatically

    Example:
        >>> import yaml2plot as y2p
        >>> y2p.set_renderer("notebook")  # Force notebook inline display
        >>> y2p.set_renderer("browser")   # Force browser display
        >>> y2p.set_renderer("auto")      # Auto-detect (default)
    """
    if renderer == "auto":
        configure_plotly_renderer()
    else:
        pio.renderers.default = renderer

    print(f"📊 Plotly renderer set to: {pio.renderers.default}")


__all__ = [
    # Main API
    "plot",
    "load_spice_raw",
    "load_spice_raw_batch",
    "load_csv_data",
    "load_csv_data_batch",
    # Core classes
    "PlotSpec",
    "WaveDataset",
    # Utilities
    "set_renderer",
    "pio",  # Give users access to plotly.io
]

# Configure Plotly renderer automatically on import
# This eliminates the need for manual renderer configuration in user code
try:
    configure_plotly_renderer()
except Exception:
    # If auto-detection fails, default to browser (safe fallback)
    pio.renderers.default = "browser"
