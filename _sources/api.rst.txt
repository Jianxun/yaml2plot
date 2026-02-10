API Reference
=============

yaml2plot 2.0.1 exposes a streamlined, function-oriented public API built around three explicit steps:

1. **Data Loading** – Load raw SPICE data into Python with :func:`yaml2plot.load_spice_raw` *or* let :func:`yaml2plot.plot` load it lazily from a file path.
2. **Configuration** – Describe what you want to plot using :class:`yaml2plot.PlotSpec` (YAML, file, or dictionary input).
3. **Plotting** – Call :func:`yaml2plot.plot` to generate an interactive Plotly figure.

This page documents each public symbol in the order you will use them.

Coordinate Inference (`load_spice_raw`)
----------------------------------------

When building an ``xarray.Dataset`` from a SPICE ``.raw`` file, coordinate selection is deterministic:

1. Use ``time`` if present.
2. Otherwise use ``frequency`` if present.
3. Otherwise use the first signal as a fallback coordinate (dimension name ``axis``).

Warnings:

* If both ``time`` and ``frequency`` are present, ``time`` is chosen and a ``UserWarning`` is emitted.
* If neither canonical coordinate exists, the first-signal fallback is used and a ``UserWarning`` is emitted.

Main API Symbols
----------------

.. currentmodule:: yaml2plot

.. autosummary::
   :toctree: _autosummary

   plot
   load_spice_raw
   load_spice_raw_batch
   load_csv_data
   load_csv_data_batch
   PlotSpec
   WaveDataset
