import numpy as np
import plotly.graph_objects as go
import pytest
import xarray as xr
from pathlib import Path
from unittest.mock import patch

from yaml2plot.core.plotting import (
    _calculate_y_axis_domains,
    _config_zoom,
    add_waveform,
    create_figure,
    plot,
)
from yaml2plot.core.plotspec import PlotSpec


class TestCalculateYAxisDomains:
    """Tests for the _calculate_y_axis_domains helper."""

    def test_single_axis_returns_full_domain(self):
        """A single Y-axis should occupy the full [0, 1] domain."""
        assert _calculate_y_axis_domains(1) == [[0, 1]]

    def test_two_axes_are_evenly_split_with_gap(self):
        """Two Y-axes should share the space with a 0.05 gap in between.

        Expected domains are computed from the same algorithm to avoid hard-coding
        magic numbers, but the top axis must be above the bottom one and the
        domains must not overlap.
        """
        domains = _calculate_y_axis_domains(2)

        # There must be exactly two domains
        assert len(domains) == 2

        # Domains should be ordered from top to bottom
        top, bottom = domains
        # The upper part of the bottom axis must be below the lower bound of the top axis
        assert bottom[1] <= top[0]

        # Both domains should lie within [0, 1]
        for d in domains:
            assert 0.0 <= d[0] <= 1.0
            assert 0.0 <= d[1] <= 1.0

        # Height of each axis should be identical
        top_height = top[1] - top[0]
        bottom_height = bottom[1] - bottom[0]
        assert pytest.approx(top_height, rel=1e-9) == bottom_height


class TestConfigZoom:
    """Tests for the _config_zoom helper."""

    def test_zero_axes_returns_empty_dict(self):
        assert _config_zoom({}, 0) == {}

    def test_zoom_settings_are_set_for_multiple_axes(self):
        cfg = _config_zoom({}, 3)

        # Basic keys present
        assert cfg["dragmode"] == "zoom"
        assert cfg["xaxis.fixedrange"] is False

        # yaxis.fixedrange entries for every axis
        for idx in range(3):
            axis_id = "yaxis" if idx == 0 else f"yaxis{idx + 1}"
            assert cfg[f"{axis_id}.fixedrange"] is False


class TestAddWaveform:
    """Tests for add_waveform convenience wrapper."""

    def test_adds_trace_and_preserves_y_axis_assignment(self):
        x = np.array([0, 1, 2])
        y = np.array([10, 11, 12])
        fig = create_figure()

        # Add to the default axis first
        add_waveform(fig, x, y, name="default")
        assert len(fig.data) == 1
        assert fig.data[0].yaxis == "y"

        # Add to a secondary axis
        add_waveform(fig, x, y, name="secondary", y_axis="y2", line_color="red")
        assert len(fig.data) == 2
        assert fig.data[1].yaxis == "y2"
        # Extra kwargs should be forwarded (e.g. line color)
        assert fig.data[1].line.color == "red"


class TestPlotFilePathHandling:
    """Test plot() function with file path input using xarray Dataset API."""
    
    def test_plot_with_file_path_converts_xarray_dataset(self, tmp_path):
        """Test that plot() correctly handles file paths with new xarray Dataset API."""
        # Create a mock file
        test_file = tmp_path / "test.raw"
        test_file.write_text("dummy")
        
        # Create a mock xarray Dataset
        mock_dataset = xr.Dataset(
            data_vars={
                "v(out)": (["time"], np.array([0.0, 0.9, 1.8])),
                "v(in)": (["time"], np.array([1.8, 1.8, 1.8]))
            },
            coords={"time": np.array([0.0, 1e-9, 2e-9])},
            attrs={"analysis_type": "transient"}
        )
        
        # Create a simple plot spec
        spec = PlotSpec.from_yaml("""
        title: "Test Plot"
        x: {signal: "time"}
        y:
          - label: "Voltage (V)"
            signals: {Output: "v(out)"}
        """)
        
        # Mock load_spice_raw to return xarray Dataset
        with patch("yaml2plot.loader.load_spice_raw", return_value=mock_dataset):
            fig = plot(test_file, spec, show=False)
            
        # Verify the plot was created correctly
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].name == "Output"
        
        # Verify the data matches our mock dataset
        np.testing.assert_array_equal(fig.data[0].x, [0.0, 1e-9, 2e-9])
        np.testing.assert_array_equal(fig.data[0].y, [0.0, 0.9, 1.8])


class TestPlotDataFrameHandling:
    def test_plot_accepts_pandas_dataframe_with_named_index(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"vout": [0.0, 0.9], "vin": [1.8, 1.8]}, index=[0.0, 1e-9])
        df.index.name = "time"

        spec = PlotSpec.from_yaml("""
        title: "DataFrame Input"
        x: {signal: "time"}
        y:
          - label: "Voltage (V)"
            signals: {Output: "vout"}
        """)

        fig = plot(df, spec, show=False)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        np.testing.assert_array_equal(fig.data[0].x, [0.0, 1e-9])
        np.testing.assert_array_equal(fig.data[0].y, [0.0, 0.9])

    def test_plot_accepts_dataframe_with_index_alias(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame({"vout": [0.0, 0.9]}, index=[0, 1])

        spec = PlotSpec.from_yaml("""
        x: {signal: "index"}
        y:
          - label: "Voltage (V)"
            signals: {Output: "vout"}
        """)

        fig = plot(df, spec, show=False)
        np.testing.assert_array_equal(fig.data[0].x, [0, 1])


class TestPlotCsvPathRouting:
    def test_csv_path_uses_csv_loader(self, tmp_path):
        pd = pytest.importorskip("pandas")
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("time,vout\n0,0.0\n1e-9,0.9\n")
        df = pd.read_csv(csv_file)

        spec = PlotSpec.from_yaml("""
        x: {signal: "time"}
        y:
          - label: "Voltage (V)"
            signals: {Output: "vout"}
        """)

        with patch("yaml2plot.loader.load_csv_data", return_value=df) as m_csv, patch(
            "yaml2plot.loader.load_spice_raw"
        ) as m_raw:
            fig = plot(csv_file, spec, show=False)

        assert isinstance(fig, go.Figure)
        m_csv.assert_called_once_with(csv_file)
        m_raw.assert_not_called()
