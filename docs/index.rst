.. yaml2plot documentation master file, created by
   sphinx-quickstart on Tue Jun 10 12:19:18 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

yaml2plot: A Python Toolkit for SPICE Simulation Waveform Visualization
========================================================================

*yaml2plot* is a modern Python toolkit for turning raw SPICE ``.raw`` files into beautiful, interactive Plotly graphs. It provides two powerful workflows to get from simulation data to interactive plots:

* **CLI-First Workflow** – The fastest way to get from a ``.raw`` file to an interactive plot using the ``y2p`` command-line tool
* **Python API Workflow** – Full programmatic control for custom analysis, scripting, and Jupyter integration

Features
--------

* **Interactive Plotly Visualization** – Modern, web-based plots with zoom, pan, and hover
* **Command Line Interface** – Quick plotting from terminal with ``y2p plot`` 
* **Flexible data API** – supports ``xarray.Dataset`` (``load_spice_raw``), dict-like mappings, pandas ``DataFrame`` inputs, and ``.raw``/``.csv`` path routing via ``plot()``
* **YAML-first configuration** – version-controlled plot specs that live next to your simulations
* **Processed-data integration** – mix NumPy-derived signals with raw traces in a single call
* **Automatic renderer detection** – works seamlessly in Jupyter, VS Code, or standalone scripts

Quick Start: CLI Workflow
--------------------------

Get from a raw file to a plot in three steps using the ``y2p`` command-line tool.

**Step 1: Generate a Plot Specification**

Use ``y2p init`` to create a template ``spec.yaml`` file from your simulation output:

.. code-block:: bash

   y2p init your_simulation.raw > spec.yaml

**Step 2: Discover Signals** 

Find the exact names of the signals you want to plot:

.. code-block:: bash

   # List the first 10 signals
   y2p signals your_simulation.raw

   # List all signals  
   y2p signals your_simulation.raw --all

   # Filter signals using a regular expression
   y2p signals your_simulation.raw --grep "clk"

**Step 3: Plot**

Edit your ``spec.yaml`` to include the signals you discovered, then generate an interactive plot:

.. code-block:: bash

   # This command will open a browser window with your plot
   y2p plot spec.yaml

   # You can also override the raw file specified in the YAML
   y2p plot spec.yaml your_simulation.raw

   # To save the plot to a file instead
   y2p plot spec.yaml --output my_plot.html

This approach is fast, requires no Python code, and keeps your plot configuration version-controlled alongside your simulation files.

Quick Start: Python API
------------------------

For advanced use cases, the Python API provides full control over data loading, processing, and plotting:

.. code-block:: python

   import yaml2plot as y2p

   # 1. Load data from a .raw file
   dataset = y2p.load_spice_raw("your_simulation.raw")
   print(f"Signals available: {list(dataset.data_vars)[:5]}...")

   # 2. Configure the plot using a YAML string
   spec = y2p.PlotSpec.from_yaml("""
   title: "My Simulation Results"
   x:
     signal: "time"
     label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         Output: "v(out)"
         Input:  "v(in)"
   """)

   # 3. Create and display the plot
   fig = y2p.plot(dataset, spec)
   fig.show()

**Advanced Example: Plotting Derived Signals**

With xarray Dataset integration, you can easily perform calculations and plot derived signals:

.. code-block:: python

   import numpy as np
   import yaml2plot as y2p

   # Load the data as xarray Dataset
   dataset = y2p.load_spice_raw("your_simulation.raw")

   # Calculate derived signals directly on the Dataset
   dataset["diff_voltage"] = dataset["v(out_p)"] - dataset["v(out_n)"]
   dataset["power"] = dataset["v(out)"] ** 2

   # Create a spec that plots both raw and derived signals
   spec = y2p.PlotSpec.from_yaml("""
   title: "Differential Output Analysis"
   x:
     signal: "time"
     label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         VOUT_P: "v(out_p)"
         VOUT_N: "v(out_n)"
         VOUT_DIFF: "diff_voltage"
     - label: "Power (W)"
       signals:
         Power: "power"
   """)

   # Create and display the plot
   fig = y2p.plot(dataset, spec)
   fig.show()

Installation
------------

.. code-block:: bash

   pip install yaml2plot

For development:

.. code-block:: bash

   pip install -e ".[dev]"

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   configuration
   schema
   cli
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api

.. toctree::
   :maxdepth: 1
   :caption: Development:

   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
