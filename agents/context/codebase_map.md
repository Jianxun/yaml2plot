# Codebase Map

## Top-level navigation
- `src/yaml2plot/`: package implementation.
- `tests/`: unit and workflow tests.
- `docs/`: Sphinx docs source.
- `.github/workflows/`: CI/CD definitions.
- `context/`: legacy session-memory files (historical reference).
- `agents/`: multi-agent roles and canonical planning context.

## Core package files
- `src/yaml2plot/__init__.py`: public exports and renderer setup.
- `src/yaml2plot/loader.py`: raw-file loading to `xarray.Dataset`.
- `src/yaml2plot/cli.py`: Click CLI (`y2p`).
- `src/yaml2plot/core/plotspec.py`: Pydantic YAML schema.
- `src/yaml2plot/core/plotting.py`: figure creation and axis/layout helpers.
- `src/yaml2plot/core/wavedataset.py`: wrapper over `spicelib.RawRead`.
- `src/yaml2plot/utils/env.py`: environment-aware Plotly renderer configuration.

## Tests by subsystem
- CLI tests: `tests/unit/cli/`.
- Loader tests: `tests/unit/loader/`.
- PlotSpec tests: `tests/unit/plotspec/`.
- Plotting tests: `tests/unit/plotting/`.
- WaveDataset tests: `tests/unit/wavedataset/`.
- End-to-end workflows: `tests/workflows/`.
- Test fixture raw files: `tests/raw_files/`.

## Build, packaging, and quality
- `pyproject.toml`: package metadata, dependencies, pytest/mypy/isort/black config.
- `requirements.txt` / `requirements-dev.txt`: pinned dependency lists.
- `Makefile`: dev/test/docs convenience commands.

## CI/CD
- `.github/workflows/test.yml`: matrix test workflow.
- `.github/workflows/docs.yml`: docs build/deploy workflow.
- `.github/workflows/publish.yml`: PyPI publish on release.

## Workflow context (canonical)
- `agents/context/contract.md`
- `agents/context/tasks.yaml`
- `agents/context/tasks_state.yaml`
- `agents/context/tasks_icebox.yaml`
- `agents/context/tasks_archived.yaml`
- `agents/context/project_status.md`
- `agents/context/lessons.md`
