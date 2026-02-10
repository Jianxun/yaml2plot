from pathlib import Path

import plotly.graph_objects as go
import pytest
import yaml2plot as y2p


class TestCsvPlotWorkflow:
    """User story: plot directly from CSV path using yaml2plot.plot."""

    def test_plot_from_csv_path(self, tmp_path):
        pytest.importorskip("pandas")

        csv_file = tmp_path / "signals.csv"
        csv_file.write_text("time,vout,vin\n0,0.0,1.8\n1e-9,0.9,1.8\n")

        spec = y2p.PlotSpec.from_yaml(
            """
            title: "CSV Workflow"
            x:
              signal: "time"
            y:
              - label: "Voltage (V)"
                signals:
                  Output: "vout"
                  Input: "vin"
            """
        )

        fig = y2p.plot(Path(csv_file), spec, show=False)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
