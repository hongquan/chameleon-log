🦎 ChameleonLog Documentation
==============================

ChameleonLog provides colorful, structured logging for Python applications using the `Logbook`_ framework.

🌟 Features
============

- **RichHandler**: Beautiful console output with syntax highlighting and tracebacks using the `Rich`_ library
- **JournaldHandler**: Structured logging to `systemd`_ `journald`_ with automatic level-based coloring and filtering
- **SentryHandler**: Error tracking and crash reporting to `Sentry`_

.. _logbook: https://pypi.org/project/Logbook/
.. _Rich: https://pypi.org/project/rich/
.. _systemd: https://systemd.io/
.. _journald: https://systemd.io/
.. _Sentry: https://sentry.io/

📦 Installation
================

Install ChameleonLog using ``pip``:

.. code-block:: bash

    pip install chameleon-log

Or using ``uv``:

.. code-block:: bash

    uv add chameleon-log

🔧 Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

To use the :py:class:`~chameleon_log.journald.JournaldHandler` for sending logs to systemd journald (Linux only):

.. code-block:: bash

    pip install chameleon-log[journald]

Or using uv:

.. code-block:: bash

    uv add chameleon-log --extra journald

This will also install the `journald-send`_ package, requiring systemd-based Linux distros.

To use the :py:class:`~chameleon_log.sentry.SentryHandler` for forwarding errors to Sentry:

.. code-block:: bash

    pip install chameleon-log[sentry]

Or using uv:

.. code-block:: bash

    uv add chameleon-log --extra sentry

This will also install the `sentry-sdk`_ package.

.. _journald-send: https://pypi.org/project/journald-send/
.. _sentry-sdk: https://pypi.org/project/sentry-sdk/

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
