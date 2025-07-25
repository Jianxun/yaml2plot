# %%
import yaml2plot as y2p

# Use the test data we have available
spice_file = "./raw_data/Ring_Oscillator_7stage.raw"

dataset = y2p.load_spice_raw(spice_file)

spec = y2p.PlotSpec.from_yaml("""
title: "Ring Oscillator - Key Nodes"

X:
  signal: "time"
  label: "Time (s)"

Y:
  - label: "Voltages (V)"
    signals:
      Bus06: "v(bus06)"
      Bus07: "v(bus07)"
      
  - label: "Current (A)"
    signals:
      Supply Current: "i(c1)"

width: 900
height: 600
show_rangeslider: true
""")

fig1 = y2p.plot(dataset, spec)

# %%
