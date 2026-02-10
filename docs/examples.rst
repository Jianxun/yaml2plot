Examples
========

.. note::
   All code below targets *yaml2plot* **2.0.1**.  The modern workflow is:

   1. ``data = y2p.load_spice_raw("my.raw")`` – obtain an ``xarray.Dataset`` with signals and metadata
   2. ``spec = y2p.PlotSpec.from_yaml(""" ... """)`` – build a PlotSpec (YAML string or file)
   3. ``fig = y2p.plot(data, spec)`` – create the Plotly figure

This page contains practical examples for common use cases with yaml2plot.

Basic Waveform Plot
-------------------

Plot input and output voltages from an amplifier simulation:

.. code-block:: python

   import yaml2plot as y2p

   # Load simulation data
   data = y2p.load_spice_raw("amplifier.raw")

   # Simple voltage plot using YAML configuration
   spec = y2p.PlotSpec.from_yaml("""
   title: "Amplifier Response"
   x:
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         Input: "v(in)"
         Output: "v(out)"
   """)

   fig = y2p.plot(data, spec)

Multi-Y-Axis Plot
-----------------

Create multiple strips with shared x-axis and rangeslider:

.. code-block:: python

   data = y2p.load_spice_raw("complete_analysis.raw")

   spec = y2p.PlotSpec.from_yaml("""
   title: "Complete Circuit Analysis"
   x:
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         Input: "v(in)"
         Output: "v(out)"
     - label: "Current (A)"
       signals:
         M1: "i(m1)"
         M2: "i(m2)"
     - label: "Supply Voltage (V)"
       signals:
         VDD: "v(vdd)"
         VSS: "v(vss)"
    show_rangeslider: true
   """)

   fig = y2p.plot(data, spec)

AC Analysis with Complex Signal Processing
--------------------------------------------

AC analysis results contain complex numbers for voltage and current signals, enabling proper 
magnitude and phase analysis for transfer functions and Bode plots:

.. code-block:: python

   import yaml2plot as y2p
   import numpy as np

   # Load AC analysis data (contains complex numbers)
   data = y2p.load_spice_raw("ac_analysis.raw")
   
   tf = data["v(out)"]/data["v(in)"]
   data["tf_db"] = 20*np.log10(np.abs(tf))
   data["tf_phase"] = np.angle(tf)/np.pi*180

   spec = y2p.PlotSpec.from_yaml("""
   title: "Transfer Function Bode Plot"
   x:
    signal: "frequency"
    label: "Frequency (Hz)"
    scale: "log"
   y:
     - label: "Magnitude (dB)"
       signals:
         H(jω): "tf_db"
     - label: "Phase (degrees)"
       signals:
         φ(jω): "tf_phase"
   height: 800
   show_rangeslider: true
   """)

   fig = y2p.plot(data, spec)

Comparison Plots
----------------

Compare results from different simulation runs:

.. code-block:: python

   import xarray as xr
   # Load multiple simulations
   data1 = y2p.load_spice_raw("before_optimization.raw")
   data2 = y2p.load_spice_raw("after_optimization.raw")

   # Create comparison signals
   data = xr.Dataset()
   data["v_out_before"] = data1["v(out)"]
   data["v_out_after"] = data2["v(out)"]

   spec = y2p.PlotSpec.from_yaml("""
   title: "Optimization Comparison"
   x:
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals:
         Before: "v_out_before"
         After: "v_out_after"
   """)

   fig = y2p.plot(data, spec) 
