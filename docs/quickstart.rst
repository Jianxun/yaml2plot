Quick Start Guide
=================

This guide provides two common workflows for using ``y2p`` to visualize your SPICE simulations.

* **Option A: CLI-First** – The fastest way to get from a ``.raw`` file to an interactive plot. Perfect for quick, one-off visualizations.
* **Option B: Python API** – The most flexible approach. Ideal for scripting, custom data processing, and embedding plots in notebooks or reports.

Choose the workflow that best fits your needs.

Option A: CLI-First Workflow
----------------------------

Get from a raw file to a plot in three steps using the ``y2p`` command-line tool.

**Step 1: Generate a Plot Specification**

Use ``y2p init`` to create a template ``spec.yaml`` file from your simulation output. It automatically populates the file with the independent variable (like "time") and a few available signals.

.. code-block:: bash

   y2p init your_simulation.raw > spec.yaml

**Step 2: Discover Signals**

Find the exact names of the signals you want to plot with ``y2p signals``.

.. code-block:: bash

   # List the first 10 signals
   y2p signals your_simulation.raw

   # List all signals
   y2p signals your_simulation.raw --all

   # Filter signals using a regular expression
   y2p signals your_simulation.raw --grep "v(out)"

**Step 3: Plot**

Edit your ``spec.yaml`` to include the signals you discovered, then use ``y2p plot`` to generate an interactive HTML file or display the plot directly.

.. code-block:: bash

   # This command will open a browser window with your plot
   y2p plot spec.yaml

   # To save the plot to a file instead
   y2p plot spec.yaml --output my_plot.html

This approach is fast, requires no Python code, and keeps your plot configuration version-controlled alongside your simulation files.

Option B: Python API Workflow
-----------------------------

For more advanced use cases, the Python API provides full control over data loading, processing, and plotting. This is ideal for Jupyter notebooks, custom analysis scripts, and automated report generation.

The API follows a clear three-step workflow:

1.  **Data Loading** – Load the raw ``.raw`` file with :func:`yaml2plot.load_spice_raw`, load tabular data with :func:`yaml2plot.load_csv_data`, or pass file paths directly to :func:`yaml2plot.plot`.
2.  **Configuration** – Describe what you want to see using :class:`yaml2plot.PlotSpec`.
3.  **Plotting** – Call :func:`yaml2plot.plot` to get a Plotly figure.

**Minimal Example**

.. code-block:: python

   import yaml2plot as y2p

   # 1. Load data from a .raw file (returns xarray.Dataset)
   data = y2p.load_spice_raw("your_simulation.raw")
   print(f"Signals available: {list(data.data_vars)[:5]}...")

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
   fig = y2p.plot(data, spec)
   fig.show()

**Advanced Example: Plotting Derived Signals**

Because the API gives you direct access to loaded data, you can easily perform calculations and plot the results.

.. code-block:: python

   import numpy as np
   import yaml2plot as y2p

   # Load the data and build a dict view for derived signals
   dataset = y2p.load_spice_raw("your_simulation.raw")
   data = {name: dataset[name].values for name in dataset.data_vars}
   data["time"] = dataset.coords["time"].values

   # Calculate a new, derived signal
   data["diff_voltage"] = data["v(out_p)"] - data["v(out_n)"]

   # Create a spec that plots both raw and derived signals
   spec = y2p.PlotSpec.from_yaml("""
   title: "Differential Output Voltage"
   x:
     signal: "time"
     label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         VOUT_P: "v(out_p)"
         VOUT_N: "v(out_n)"
         VOUT_DIFF: "diff_voltage"
   """)

   # Create and display the plot
   fig = y2p.plot(data, spec)
   fig.show()

**DataFrame and CSV Inputs**

.. code-block:: python

   import yaml2plot as y2p

   # Option 1: load CSV into a DataFrame explicitly
   df = y2p.load_csv_data("signals.csv")
   fig = y2p.plot(df, spec)

   # Option 2: let plot() route ".csv" path inputs automatically
   fig = y2p.plot("signals.csv", spec)

For DataFrame inputs, ``x.signal`` can reference:

* a DataFrame column name
* the DataFrame index name
* ``index`` as a generic alias for the DataFrame index

Next Steps
----------

*   Dive into the :doc:`configuration` guide for all available YAML options.
*   Browse the :doc:`cli` reference for more command-line features.
*   Consult the :doc:`api` reference for full details on each function. 
