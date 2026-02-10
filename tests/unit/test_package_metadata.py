from pathlib import Path
import re
import importlib

import plotly.io as pio
import yaml2plot as y2p


def _pyproject_version() -> str:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
    assert match is not None, "project.version not found in pyproject.toml"
    return match.group(1)


def test_runtime_version_matches_pyproject() -> None:
    assert y2p.__version__ == _pyproject_version()


def test_public_api_exports_csv_helpers() -> None:
    exported = set(y2p.__all__)
    assert "load_csv_data" in exported
    assert "load_csv_data_batch" in exported


def test_import_does_not_mutate_plotly_renderer_default() -> None:
    original = pio.renderers.default
    try:
        pio.renderers.default = "json"
        importlib.reload(y2p)
        assert pio.renderers.default == "json"
    finally:
        pio.renderers.default = original
        importlib.reload(y2p)
