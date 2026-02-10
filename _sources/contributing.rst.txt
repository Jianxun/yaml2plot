Contributing
============

We welcome contributions to yaml2plot! This guide will help you get started.

Development Setup
-----------------

1. **Fork and Clone**:

.. code-block:: bash

   git clone https://github.com/Jianxun/yaml2plot.git
   cd yaml2plot

2. **Create Virtual Environment**:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Development Dependencies**:

.. code-block:: bash

   pip install -e ".[dev]"

4. **Run Tests**:

.. code-block:: bash

   pytest

Development Workflow
--------------------

We follow a test-driven development approach:

1. **Write Tests First**: Define expected behavior with tests
2. **Implement Features**: Write minimal code to pass tests  
3. **Run Tests**: Verify functionality
4. **Refactor**: Improve code while maintaining test coverage

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=yaml2plot
   
   # Run specific test file
   pytest tests/test_api.py
   
   # Run specific test
   pytest tests/test_api.py::test_plot_basic

Code Quality
~~~~~~~~~~~~

We use several tools to maintain code quality:

.. code-block:: bash

   # Format code
   black src/ tests/
   
   # Sort imports
   isort src/ tests/
   
   # Lint code
   flake8 src/ tests/
   
   # Type checking
   mypy src/

Pre-commit Hooks
~~~~~~~~~~~~~~~~

Set up pre-commit hooks to automatically check code:

.. code-block:: bash

   pre-commit install

This will run formatting, linting, and type checking before each commit.

Contributing Guidelines
-----------------------

Code Style
~~~~~~~~~~

* Follow PEP 8 style guidelines
* Use type hints for all functions
* Write descriptive docstrings
* Prefer explicit over implicit code
* Use meaningful variable and function names

Testing
~~~~~~~

* All new features must have tests
* Maintain or improve test coverage
* Test both success and error conditions
* Use descriptive test names that explain the scenario

Documentation
~~~~~~~~~~~~~

* Update documentation for new features
* Include code examples in docstrings
* Keep README.md up to date
* Add entries to CHANGELOG.md

Pull Request Process
--------------------

1. **Create Feature Branch**:

.. code-block:: bash

   git checkout -b feature/your-feature-name

2. **Make Changes**:
   
   * Write tests first
   * Implement feature
   * Update documentation
   * Run tests and quality checks

3. **Commit Changes**:

.. code-block:: bash

   git add .
   git commit -m "feat: add your feature description"

Use conventional commit format:

* ``feat:`` for new features
* ``fix:`` for bug fixes  
* ``docs:`` for documentation
* ``test:`` for tests
* ``refactor:`` for refactoring

4. **Push and Create PR**:

.. code-block:: bash

   git push origin feature/your-feature-name

Then create a pull request on GitHub.

Architecture Guidelines
-----------------------

Core Principles
~~~~~~~~~~~~~~~

* **Explicit Configuration**: Prefer explicit PlotSpec/data inputs while keeping practical auto-detection where documented
* **Path Object Support**: Use ``pathlib.Path`` throughout
* **Comprehensive Validation**: Clear error messages guide users
* **Test-Driven Development**: Tests define expected behavior

Module Organization
~~~~~~~~~~~~~~~~~~~

* ``src/yaml2plot/`` – Public package root.
* ``src/yaml2plot/__init__.py`` – Public API exports (``plot``, ``PlotSpec``, ``WaveDataset``, ``load_spice_raw``, ``load_spice_raw_batch``, ``load_csv_data``, ``load_csv_data_batch``, ``set_renderer``).
* ``src/yaml2plot/core/plotspec.py`` – Pydantic model that defines the PlotSpec schema.
* ``src/yaml2plot/core/plotting.py`` – Function-based plotting helpers and ``plot``.
* ``src/yaml2plot/core/wavedataset.py`` – Thin wrapper around ``spicelib`` for fast raw-file loading.
* ``src/yaml2plot/loader.py`` – Convenience wrappers for SPICE raw and CSV loading helpers.
* ``src/yaml2plot/cli.py`` – Command-line interface built on the current v2.x API.
* ``src/yaml2plot/utils/`` – Small internal utilities (e.g. ``env.py`` for renderer selection).

Legacy files (``reader.py``, ``config.py``, ``plotter.py``) were removed in 1.0.0 – do **not** add code to those names.

API Design
~~~~~~~~~~

* Functions should be intuitive for first-time users
* Provide sensible defaults to minimize required parameters
* Use consistent parameter names across functions
* Support both simple and advanced use cases
* Maintain backward compatibility in minor version updates

Issue Reporting
---------------

When reporting issues:

1. **Search Existing Issues**: Check if already reported
2. **Provide Context**: Include version, Python version, OS
3. **Minimal Example**: Provide code to reproduce the issue
4. **Expected vs Actual**: Describe what you expected vs what happened

Bug Report Template
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   **Environment**:
   - yaml2plot version: 
   - Python version:
   - Operating System:
   
   **Description**:
   Brief description of the issue.
   
   **Steps to Reproduce**:
   1. 
   2. 
   3. 
   
   **Expected Behavior**:
   What you expected to happen.
   
   **Actual Behavior**:
   What actually happened.
   
   **Code Example**:
   ```python
   # Minimal code to reproduce
   ```

Feature Requests
~~~~~~~~~~~~~~~~

For feature requests:

1. **Describe the Problem**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Use Cases**: Provide specific examples of how it would be used

Getting Help
------------

* **GitHub Issues**: For bugs and feature requests
* **GitHub Discussions**: For questions and general discussion
* **Documentation**: Check the docs first

Recognition
-----------

Contributors will be recognized in:

* ``CONTRIBUTORS.md`` file
* Release notes
* Package metadata

Thank you for contributing to yaml2plot! 
