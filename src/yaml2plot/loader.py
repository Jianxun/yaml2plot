"""SPICE raw-file loading helpers for yaml2plot.

These high-level functions build on `WaveDataset` to give users a quick way to
obtain xarray Dataset objects from single SPICE *.raw* files or
from a batch of files (e.g. PVT / Monte-Carlo sweeps).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import xarray as xr

from .core.wavedataset import WaveDataset

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

__all__ = [
    "load_spice_raw",
    "load_spice_raw_batch",
    "load_csv_data",
    "load_csv_data_batch",
]

_PathLike = Union[str, Path]


def _validate_file_path(path: _PathLike, *, kind: str = "file") -> Path:
    """Return a *Path* after validating type, emptiness, and existence."""
    if path is None:
        raise TypeError("file path must be a string or Path object, not None")

    if isinstance(path, str) and path.strip() == "":
        raise ValueError("file path cannot be empty")

    if not isinstance(path, (str, Path)):
        raise TypeError("file path must be a string or Path object")

    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"{kind} not found: {file_path}")

    return file_path


# ────────────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────────────


def load_spice_raw(raw_file: _PathLike) -> xr.Dataset:
    """Load one SPICE *.raw* file and return an xarray Dataset."""
    file_path = _validate_file_path(raw_file, kind="SPICE raw file")

    wave_data = WaveDataset.from_raw(str(file_path))
    
    # Create xarray Dataset
    data_vars = {}
    coords = {}
    attrs = {}
    
    # Get all signals
    signals = wave_data.signals
    
    # Find coordinate axis (time, frequency, or first signal)
    coord_signal = None
    dim_name = None
    
    if 'time' in [s.lower() for s in signals]:
        coord_signal = next(s for s in signals if s.lower() == 'time')
        dim_name = 'time'
    elif 'frequency' in [s.lower() for s in signals]:
        coord_signal = next(s for s in signals if s.lower() == 'frequency')
        dim_name = 'frequency'
    else:
        # Fallback: use first signal as coordinate
        coord_signal = signals[0]
        dim_name = 'axis'
    
    # Add coordinate
    coord_data = wave_data.get_signal(coord_signal)
    coords[dim_name] = coord_data
    
    # Add all other signals as data variables
    for signal in signals:
        if signal != coord_signal:
            data_vars[signal] = ([dim_name], wave_data.get_signal(signal))
    
    # Add metadata as global attributes
    attrs.update(wave_data.metadata)
    
    return xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)


def load_spice_raw_batch(
    raw_files: List[_PathLike],
) -> List[xr.Dataset]:
    """Load many *.raw* files, preserving the order, and return a list of xarray Datasets."""
    if raw_files is None:
        raise TypeError("raw_files must be a list of file paths, not None")

    if not isinstance(raw_files, (list, tuple)):
        raise TypeError("raw_files must be a list or tuple of file paths")

    return [load_spice_raw(p) for p in raw_files]


def load_csv_data(
    csv_file: _PathLike,
    *,
    x_column: Optional[str] = None,
) -> "pd.DataFrame":
    """Load one CSV file and return a pandas DataFrame."""
    if not HAS_PANDAS:
        raise ImportError(
            "pandas is required for CSV loading. Install pandas to use load_csv_data."
        )

    file_path = _validate_file_path(csv_file, kind="CSV file")
    dataframe = pd.read_csv(file_path)

    if x_column is not None:
        if x_column not in dataframe.columns:
            raise ValueError(
                f"x_column '{x_column}' not found in CSV columns: {list(dataframe.columns)}"
            )
        dataframe = dataframe.set_index(x_column, drop=False)

    return dataframe


def load_csv_data_batch(
    csv_files: List[_PathLike],
) -> List["pd.DataFrame"]:
    """Load many CSV files and return a list of pandas DataFrames."""
    if csv_files is None:
        raise TypeError("csv_files must be a list of file paths, not None")

    if not isinstance(csv_files, (list, tuple)):
        raise TypeError("csv_files must be a list or tuple of file paths")

    return [load_csv_data(p) for p in csv_files]
