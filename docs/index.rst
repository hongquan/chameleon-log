🦎 ChameleonLog Documentation
==============================

ChameleonLog provides colorful, structured logging for Python applications using the `Logbook`_ framework.

🌟 Features
============

- **RichHandler**: Beautiful console output with syntax highlighting and tracebacks using the `Rich`_ library
- **JournaldHandler**: Structured logging to `systemd`_ `journald`_ with automatic level-based coloring and filtering

.. _logbook: https://pypi.org/project/Logbook/
.. _Rich: https://pypi.org/project/rich/
.. _systemd: https://systemd.io/
.. _journald: https://systemd.io/

📦 Installation
================

Install ChameleonLog using ``pip``:

.. code-block:: bash

    pip install chameleon_log

Or using ``uv``:

.. code-block:: bash

    uv add chameleon_log

🔧 Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

To use the :py:class:`~chameleon_log.journald.JournaldHandler` for sending logs to systemd journald (Linux only):

.. code-block:: bash

    pip install chameleon_log[journald]

Or using uv:

.. code-block:: bash

    uv add chameleon_log --extra journald

This will also install the `systemd-python`_ package, requiring systemd-based Linux distros.

.. _systemd-python: https://pypi.org/project/systemd-python/

📂 Contents
============

.. toctree::
   :maxdepth: 2
   :caption: Usage Guide

   simple
   advanced
   api-ref

🧪 Examples
============

Example code is available in the ``examples/`` directory:

- ``cli-simple.py`` - RichHandler usage with various log levels and data types
- ``journald-simple.py`` - Basic JournaldHandler usage with exception handling
- ``journald-extra-fields.py`` - Advanced JournaldHandler with structured fields
- ``auto-detect-handler.py`` - Automatic handler selection based on environment

📄 License
============

This project is licensed under the Apache License 2.0.

Logo by `Freepik <https://www.freepik.com>`_.
