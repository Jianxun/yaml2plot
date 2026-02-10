Changelog
=========

All notable changes to yaml2plot will be documented in this file.

Version 1.0.0 (2025-07-XX)
--------------------------

🚀 **Major Release – Complete API Overhaul**

⚠️ **Breaking Changes**
~~~~~~~~~~~~~~~~~~~~~~~

* **Legacy API Removed** – The following symbols no longer exist:
  * ``SpiceData`` class and ``reader.py`` module
  * ``SpicePlotter`` class and ``plotter.py`` module
  * Helper functions: ``explore_signals()``, ``load_spice()``, ``config_from_file()``, ``config_from_yaml()``, ``validate_config()``
  * Configuration model ``PlotConfig``
* **Configuration Keys Lower-cased** – ``X``/``Y`` → ``x``/``y`` for consistency.
* **Single Data Interface** – Only ``load_spice_raw`` (returns ``WaveDataset`` + dict of NumPy arrays) is supported.
* **Unified Plot Function** – ``plot()`` now accepts either a file path *or* pre-loaded data plus a ``PlotSpec``.
* **Package Namespace Trimmed** – Public API now exposes exactly four symbols: ``load_spice_raw``, ``PlotSpec``, ``plot``, and ``WaveDataset``.

🎉 **New Features & Improvements**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **PlotSpec 1.0** – Pydantic-validated model with helpers ``PlotSpec.from_yaml`` and ``PlotSpec.model_validate``.
* **Standalone Plotting Module** – Refactored ``core.plotting`` with cleaner helpers, automatic zoom config, correct Y-axis ordering, and ~75 % complexity reduction.
* **Processed-Data Integration** – Pass arbitrary NumPy arrays via ``processed_data`` for mixed raw/derived traces.
* **Complex-Number Handling** – Transparent plotting of AC analysis results; magnitude/phase examples in docs.
* **Automatic Renderer Detection** – Chooses the best Plotly renderer for Jupyter vs. CLI.
* **Higher Test Coverage** – 91 % overall (96 % plotting, 88 % PlotSpec).
* **Documentation Revamp** – Quick-start, configuration guide, API reference, and examples updated for the new workflow.

🔧 **Internal / Developer**
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Pure ``src/`` layout with zero legacy code remaining.
* Clean CLI built on ``WaveDataset`` + ``plot``.
* Extensive refactor of unit tests; legacy tests archived.

---

Version 0.1.0 (2025-01-XX)
---------------------------

**Initial Release**

Features
~~~~~~~~

* **Core API Functions**:
  
  * ``plot()`` - Main plotting function with required configuration parameter
  * ``explore_signals()`` - Signal discovery with categorized output  
  * ``load_spice()`` - SPICE file loading with Path object support
  * ``validate_config()`` - Configuration validation with helpful warnings

* **Configuration System**:

  * ``config_from_file()`` - Load configuration from YAML files
  * ``config_from_yaml()`` - Create configuration from YAML strings  
  * ``config_from_dict()`` - Create configuration from Python dictionaries
  * Multi-figure support for complex layouts
  * Comprehensive validation with clear error messages

* **SPICE Data Handling**:

  * Case-insensitive signal access (all normalized to lowercase)
  * Automatic signal categorization (voltage, current, other)
  * Modern pathlib integration throughout API
  * Support for processed data integration

* **Advanced Plotting**:

  * Plotly-based interactive plots
  * Logarithmic scale support (both X and Y axes)
  * Customizable plot titles, labels, and styling
  * Grid and legend control
  * Multi-subplot layouts

Architecture
~~~~~~~~~~~~

* **Clean 3-Step Workflow**: Discovery → Configuration → Plotting
* **Explicit over Implicit**: No hidden magic, all behavior transparent
* **Modern src/ Layout**: Ready for PyPI publication
* **Comprehensive Test Suite**: 226 tests with 92% coverage

Dependencies
~~~~~~~~~~~~

* plotly >= 5.0.0
* numpy >= 1.20.0  
* PyYAML >= 6.0
* spicelib >= 1.0.0

Supported Python
~~~~~~~~~~~~~~~~

* Python 3.8+
* Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12

Known Issues
~~~~~~~~~~~~

* None at initial release

---

**Legend**:

* 🎉 **New Features**: New functionality added
* 🐛 **Bug Fixes**: Issues resolved  
* 📝 **Documentation**: Documentation improvements
* ⚠️ **Breaking Changes**: Changes that break backward compatibility
* 🔧 **Internal**: Internal improvements not affecting public API 