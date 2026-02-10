# Contract

## Project overview
yaml2plot is a Python package that loads SPICE `.raw` simulation files and renders interactive Plotly figures using declarative YAML plot specifications and a CLI (`y2p`). The project serves both notebook and CLI-first workflows.

The current implementation uses `xarray.Dataset` as the data-loading return type while preserving plotting compatibility through internal conversion to dict-like signal arrays.

## System boundaries / components
- `src/yaml2plot/loader.py`: Public loading API (`load_spice_raw`, `load_spice_raw_batch`) returning `xarray.Dataset`.
- `src/yaml2plot/core/wavedataset.py`: Low-level wrapper over `spicelib.RawRead` for signal and metadata access.
- `src/yaml2plot/core/plotspec.py`: Pydantic models for plot schema and YAML/file parsing.
- `src/yaml2plot/core/plotting.py`: Figure/layout/trace assembly and polymorphic input normalization.
- `src/yaml2plot/cli.py`: `y2p` commands (`plot`, `init`, `signals`).
- `tests/unit/*` and `tests/workflows/*`: Unit and end-to-end behavior verification.
- `.github/workflows/*`: CI for tests, docs, publish.

## Interfaces & data contracts
- Python API:
  - `load_spice_raw(path) -> xarray.Dataset`
  - `plot(data, spec, show=True) -> plotly.graph_objects.Figure`
  - `PlotSpec.from_yaml(...)` and `PlotSpec.from_file(...)`
- CLI API:
  - `y2p plot SPEC [RAW] [--raw RAW] [--output ...]`
  - `y2p init RAW`
  - `y2p signals RAW [--limit N|--all|--grep REGEX]`
- Spec format:
  - YAML with top-level `x`, `y`, and optional `title/raw/theme/width/height/...`
  - `y` is a list of axes; each axis has `label` and `signals` map.

## Invariants (MUST / MUST NOT)
- MUST keep `load_spice_raw` returning `xarray.Dataset` for public API consistency.
- MUST preserve case-insensitive signal retrieval from SPICE traces.
- MUST keep CLI raw selection precedence: `--raw` > positional raw arg > YAML `raw` field.
- MUST keep task status source of truth in `agents/context/tasks_state.yaml` only.
- MUST NOT mix generated artifacts (`__pycache__`, `htmlcov`, `coverage.xml`) into functional commits unless explicitly needed.
- MUST NOT introduce breaking contract changes without adding rationale, migration steps, and version notes in this contract decision log.

## Verification protocol
- Environment/setup:
  - `make dev`
- Core validation:
  - `make test`
- Focused verification (when touching specific areas):
  - `pytest tests/unit/loader -v`
  - `pytest tests/unit/cli -v`
  - `pytest tests/workflows -v`
- Quality checks (as needed by task DoD):
  - `black src tests`
  - `isort src tests`
  - `flake8 src tests`
  - `mypy src/yaml2plot`
- Workflow validation:
  - `./venv/bin/python scripts/lint_tasks_state.py`

## Decision log
- 2026-02-10: Adopted multi-agent workflow files under `agents/context/*` as canonical project coordination source. Tradeoff: temporary duplication with legacy `context/*.md`; decision is to treat legacy files as historical references and keep active planning in `agents/context/*`.
- 2026-02-10: Retained `xarray.Dataset` loader return type as stable API contract to avoid another migration cycle.
