"""
Test CLI raw field functionality and override behavior.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import numpy as np

from yaml2plot.cli import cli
from yaml2plot.core.plotspec import PlotSpec


class TestCliRawFieldHandling:
    def test_plotspec_has_raw_field(self):
        """Test that PlotSpec accepts and exports raw field."""
        spec_dict = {
            "title": "Test",
            "raw": "test.raw",
            "x": {"signal": "time"},
            "y": [{"label": "V", "signals": {"V1": "v1"}}],
        }

        spec = PlotSpec.model_validate(spec_dict)
        assert spec.raw == "test.raw"

        # Test to_dict includes raw field
        config = spec.to_dict()
        assert config["raw"] == "test.raw"

    @patch("yaml2plot.cli.normalize_plot_data")
    @patch("yaml2plot.cli.create_plot")
    @patch("yaml2plot.cli.configure_plotly_renderer")
    def test_yaml_raw_field_usage(
        self, mock_configure, mock_plot, mock_normalize, tmp_path
    ):
        """Test using raw: field from YAML specification."""
        # Create a test spec file with raw: field
        spec_file = tmp_path / "spec.yaml"
        raw_file = tmp_path / "test.raw"
        raw_file.touch()  # Create empty file

        spec_content = f"""
title: "Test Plot"
raw: "{raw_file}"
x:
  signal: "time"
y:
  - label: "Voltage"
    signals:
      V1: "v1"
"""
        spec_file.write_text(spec_content)

        mock_normalize.return_value = {
            "time": np.array([1, 2, 3]),
            "v1": np.array([1, 2, 3]),
        }
        mock_plot.return_value = MagicMock()

        runner = CliRunner()
        result = runner.invoke(cli, ["plot", str(spec_file)])

        assert result.exit_code == 0
        assert f"Loading SPICE data from: {raw_file}" in result.output
        mock_normalize.assert_called_once_with(raw_file)

    @patch("yaml2plot.cli.normalize_plot_data")
    @patch("yaml2plot.cli.create_plot")
    @patch("yaml2plot.cli.configure_plotly_renderer")
    def test_positional_override_with_warning(
        self, mock_configure, mock_plot, mock_normalize, tmp_path
    ):
        """Test positional argument overrides YAML raw: field with warning."""
        spec_file = tmp_path / "spec.yaml"
        yaml_raw_file = tmp_path / "yaml.raw"
        cli_raw_file = tmp_path / "cli.raw"
        yaml_raw_file.touch()
        cli_raw_file.touch()

        spec_content = f"""
title: "Test"
raw: "{yaml_raw_file}"
x:
  signal: "time"
y:
  - label: "V"
    signals:
      V1: "v1"
"""
        spec_file.write_text(spec_content)

        mock_normalize.return_value = {
            "time": np.array([1, 2, 3]),
            "v1": np.array([1, 2, 3]),
        }
        mock_plot.return_value = MagicMock()

        runner = CliRunner()
        result = runner.invoke(cli, ["plot", str(spec_file), str(cli_raw_file)])

        assert result.exit_code == 0
        assert "Warning:" in result.output
        assert "CLI positional argument" in result.output
        assert "overrides YAML raw: field" in result.output
        assert f"Loading SPICE data from: {cli_raw_file}" in result.output
        mock_normalize.assert_called_once_with(cli_raw_file)

    @patch("yaml2plot.cli.normalize_plot_data")
    @patch("yaml2plot.cli.create_plot")
    @patch("yaml2plot.cli.configure_plotly_renderer")
    def test_raw_option_override_with_warning(
        self, mock_configure, mock_plot, mock_normalize, tmp_path
    ):
        """Test --raw option overrides both positional and YAML with warning."""
        spec_file = tmp_path / "spec.yaml"
        yaml_raw_file = tmp_path / "yaml.raw"
        pos_raw_file = tmp_path / "positional.raw"
        opt_raw_file = tmp_path / "option.raw"

        for f in [yaml_raw_file, pos_raw_file, opt_raw_file]:
            f.touch()

        spec_content = f"""
title: "Test"
raw: "{yaml_raw_file}"
x:
  signal: "time"
y:
  - label: "V"
    signals:
      V1: "v1"
"""
        spec_file.write_text(spec_content)

        mock_normalize.return_value = {
            "time": np.array([1, 2, 3]),
            "v1": np.array([1, 2, 3]),
        }
        mock_plot.return_value = MagicMock()

        runner = CliRunner()
        result = runner.invoke(
            cli, ["plot", str(spec_file), str(pos_raw_file), "--raw", str(opt_raw_file)]
        )

        assert result.exit_code == 0
        assert "Warning:" in result.output
        assert "CLI --raw option overrides" in result.output
        assert f"Loading SPICE data from: {opt_raw_file}" in result.output
        mock_normalize.assert_called_once_with(opt_raw_file)

    @patch("yaml2plot.cli.normalize_plot_data")
    @patch("yaml2plot.cli.create_plot")
    @patch("yaml2plot.cli.configure_plotly_renderer")
    def test_yaml_csv_field_usage(
        self, mock_configure, mock_plot, mock_normalize, tmp_path
    ):
        """Test using raw: field with a CSV path."""
        spec_file = tmp_path / "spec.yaml"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("time,v1\n0,1\n1,2\n")

        spec_content = f"""
title: "Test Plot"
raw: "{csv_file}"
x:
  signal: "time"
y:
  - label: "Voltage"
    signals:
      V1: "v1"
"""
        spec_file.write_text(spec_content)

        mock_normalize.return_value = {
            "time": np.array([0, 1]),
            "v1": np.array([1, 2]),
        }
        mock_plot.return_value = MagicMock()

        runner = CliRunner()
        result = runner.invoke(cli, ["plot", str(spec_file)])

        assert result.exit_code == 0
        assert f"Loading CSV data from: {csv_file}" in result.output
        mock_normalize.assert_called_once_with(csv_file)

    def test_no_raw_file_specified_error(self, tmp_path):
        """Test error when no raw file is specified anywhere."""
        spec_file = tmp_path / "spec.yaml"
        spec_content = """
title: "Test"
x:
  signal: "time"
y:
  - label: "V"
    signals:
      V1: "v1"
"""
        spec_file.write_text(spec_content)

        runner = CliRunner()
        result = runner.invoke(cli, ["plot", str(spec_file)])

        assert result.exit_code == 1
        assert "No raw file specified" in result.output
        assert "--raw option:" in result.output
        assert "Positional argument:" in result.output
        assert "Add 'raw:" in result.output
