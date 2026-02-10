from pathlib import Path
import re

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
