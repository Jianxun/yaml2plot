Configuration Guide
===================

*yaml2plot* 2.0.1 uses a single configuration model — :class:`yaml2plot.PlotSpec` — to describe everything you want to see in a plot. A PlotSpec is simply structured data (YAML, JSON, or a Python dictionary) that defines:

* **x** – which signal provides the x-axis (usually ``time`` or ``frequency``)
* **y** – one or more groups of y-axis traces
* optional figure-level options such as **title**

This page explains every option, shows practical examples, and demonstrates how to build PlotSpecs from files, strings, or dictionaries.

Creating a PlotSpec
-------------------

.. code-block:: python

   import yaml2plot as y2p

   # from a YAML file
   spec = y2p.PlotSpec.from_file("config.yaml")

   # from an inline YAML string
   spec = y2p.PlotSpec.from_yaml("""
   title: "Transient Analysis"
   x: 
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Voltage (V)"
       signals: {OUT: "v(out)"}
   """)

   # from a Python dict (raises ValidationError on mistakes)
   dict_spec = {
       "title": "Dict Example",
       "x": {"signal": "time", "label": "Time (s)"},
       "y": [{"label": "Current", "signals": {"M1": "i(m1)"}}],
   }
   spec = y2p.PlotSpec.model_validate(dict_spec)

Once you have a PlotSpec, pass it to :func:`yaml2plot.plot` together with any supported data input:

* ``xarray.Dataset`` returned by :func:`yaml2plot.load_spice_raw`
* a dict-like signal mapping
* a pandas ``DataFrame``
* a ``.raw`` or ``.csv`` path for lazy loading

Schema Reference
----------------

For the complete field-by-field documentation of all configuration options, see the :doc:`schema` reference page, which is automatically generated from the Pydantic model definitions.

Example PlotSpec
----------------

Here's a comprehensive example showing common configuration options:

.. code-block:: yaml

   title: "Amplifier Analysis"
   x: 
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Input / Output Voltage (V)"
       signals:
         VIN:  "v(in)"
         VOUT: "v(out)"
     - label: "Current (A)"
       scale: "log"
       signals:
         IM1: "i(m1)"
   
Processed / Derived Signals
---------------------------

To plot *derived* signals, add them directly to the loaded ``xarray.Dataset`` (or to a dict-like mapping if you use one) and reference them in the same PlotSpec.

.. code-block:: python

   import numpy as np, yaml2plot as y2p

   data = y2p.load_spice_raw("simulation.raw")
   power = data["v(out)"] * data["i(out)"]

   # Add the derived signal to the dataset
   data["power"] = power

   spec = y2p.PlotSpec.from_yaml("""
   x: 
    signal: "time"
    label: "Time (s)"
   y:
     - label: "Voltage & Power"
       signals:
         OUT:   "v(out)"
         Power: "power"   # shorthand for data key
   """)

   fig = y2p.plot(data, spec)

Multiple Configurations
-----------------------

For complex analyses you can create multiple PlotSpecs and call :func:`yaml2plot.plot` multiple times:

.. code-block:: python

   voltage_spec = y2p.PlotSpec.from_file("voltage.yaml")
   current_spec = y2p.PlotSpec.from_file("current.yaml")

   data = y2p.load_spice_raw("simulation.raw")
   fig_v = y2p.plot(data, voltage_spec)
   fig_i = y2p.plot(data, current_spec)

Best Practices
--------------

1. **Use descriptive labels** and include units.  
2. **Group related signals** on the same axis for easy comparison.  
3. Choose **log scales** for signals spanning many orders of magnitude.  
4. Keep YAML files next to your simulations so they can be version-controlled.

---

That's all you need to describe plots with *yaml2plot* 2.0.1. Explore the :doc:`quickstart` for an end-to-end example, or dive into :doc:`api` for full symbol documentation.
