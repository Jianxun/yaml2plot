import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import xarray as xr
from click.testing import CliRunner

import yaml2plot.cli as cli_mod


class TestApplyOverrides:
    def test_only_overrides_non_none_attributes(self):
        spec = MagicMock()
        spec.width = 400
        spec.height = 300
        # Provide some overrides (height None means keep original)
        cli_mod._apply_overrides(spec, width=800, height=None, theme="plotly_dark")
        assert spec.width == 800
        assert spec.height == 300  # unchanged
        assert spec.theme == "plotly_dark"


class TestSaveFigure:
    def _fake_fig(self):
        fig = MagicMock()
        fig.write_html = MagicMock()
        fig.write_json = MagicMock()
        fig.write_image = MagicMock()
        return fig

    @pytest.mark.parametrize(
        "suffix,writer_attr",
        [(".html", "write_html"), (".json", "write_json"), (".png", "write_image")],
    )
    def test_known_extension_calls_correct_writer(self, tmp_path, suffix, writer_attr):
        fig = self._fake_fig()
        out_file = tmp_path / f"plot{suffix}"
        cli_mod._save_figure(fig, out_file)
        getattr(fig, writer_attr).assert_called_once_with(out_file)

    def test_unknown_extension_defaults_to_html(self, tmp_path):
        fig = self._fake_fig()
        out_file = tmp_path / "plot.unknown"
        cli_mod._save_figure(fig, out_file)
        # Should fallback to HTML, with .html extension
        expected_path = out_file.with_suffix(".html")
        fig.write_html.assert_called_once_with(expected_path)


class TestSignalsCommand:
    def test_signals_lists_limited_output(self, tmp_path):
        raw_file = tmp_path / "sim.raw"
        raw_file.write_text("dummy")
        # Create mock xarray Dataset
        data_vars = {f"sig{i}": (["time"], np.array([i])) for i in range(15)}
        coords = {"time": np.array([0.0])}
        mock_dataset = xr.Dataset(data_vars=data_vars, coords=coords)
        
        with patch.object(cli_mod, "load_spice_raw", return_value=mock_dataset):
            runner = CliRunner()
            result = runner.invoke(
                cli_mod.cli, ["signals", str(raw_file), "--limit", "5"]
            )
        assert result.exit_code == 0
        # Should list only 5 signals and mention more are available
        # Note: xarray Dataset includes coordinates (time) + data variables (sig0-14) = 16 total
        assert "sig0" in result.output
        assert "sig3" in result.output  # sig4 is now beyond the limit of 5 due to time coordinate
        assert "... and 11 more signals" in result.output

    def test_signals_handles_loader_exception(self, tmp_path):
        raw_file = tmp_path / "fail.raw"
        raw_file.write_text("dummy")
        with patch.object(cli_mod, "load_spice_raw", side_effect=ValueError("boom")):
            runner = CliRunner()
            result = runner.invoke(cli_mod.cli, ["signals", str(raw_file)])
        assert result.exit_code == 1
        assert "Failed to load SPICE data: boom" in result.output


class TestPlotCommandErrorPaths:
    def test_plot_reports_data_loading_failure(self, tmp_path):
        spec_file = tmp_path / "spec.yaml"
        raw_file = tmp_path / "sim.raw"
        raw_file.touch()
        spec_file.write_text(
            f"""
title: "Test"
raw: "{raw_file}"
x:
  signal: "time"
y:
  - label: "Voltage"
    signals:
      V1: "v(out)"
"""
        )

        with patch.object(cli_mod, "normalize_plot_data", side_effect=ValueError("bad raw file")):
            runner = CliRunner()
            result = runner.invoke(cli_mod.cli, ["plot", str(spec_file)])

        assert result.exit_code == 1
        assert "Configuration Error:" not in result.output
        assert "Failed to load plotting data: bad raw file" in result.output
