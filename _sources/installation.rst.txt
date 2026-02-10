Installation
============

Requirements
------------

yaml2plot requires Python 3.8 or later and the following dependencies:

* plotly >= 5.0.0
* numpy >= 1.20.0
* PyYAML >= 6.0
* spicelib >= 1.0.0

Basic Installation
------------------

Install yaml2plot from PyPI using pip:

.. code-block:: bash

   pip install yaml2plot

Development Installation
------------------------

If you want to contribute to yaml2plot or need the latest development version:

.. code-block:: bash

   git clone https://github.com/Jianxun/yaml2plot.git
   cd yaml2plot
   pip install -e ".[dev]"

This installs yaml2plot in development mode with additional dependencies for testing and development.

Optional Dependencies
---------------------

Documentation
~~~~~~~~~~~~~

To build the documentation locally:

.. code-block:: bash

   pip install "yaml2plot[docs]"

This includes:

* sphinx >= 5.0.0
* sphinx-rtd-theme >= 1.0.0
* myst-parser >= 0.18.0

Jupyter Support
~~~~~~~~~~~~~~~

For enhanced Jupyter notebook support:

.. code-block:: bash

   pip install "yaml2plot[jupyter]"

This includes:

* ipywidgets >= 8.0.0
* jupyter >= 1.0.0
* jupyterlab >= 3.0.0

Development Tools
~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

   pip install "yaml2plot[dev]"

This includes testing, linting, and formatting tools:

* pytest >= 7.0.0
* pytest-cov >= 4.0.0
* black >= 22.0.0
* isort >= 5.0.0
* flake8 >= 4.0.0
* mypy >= 1.0.0
* pre-commit >= 2.0.0

Verification
------------

To verify your installation, run:

.. code-block:: python

   import yaml2plot as y2p
   print(y2p.__version__)

This should print the version number without any errors. 