💡 Simple Usage
=================

ChameleonLog provides two handlers for different environments: :py:class:`~chameleon_log.RichHandler` for colorful console output during development, and :py:class:`~chameleon_log.journald.JournaldHandler` for structured logging to `systemd`_ `journald`_ in production.

✨ RichHandler
================

The :py:class:`~chameleon_log.RichHandler` provides beautiful console output with syntax highlighting and formatted tracebacks for **development**.

🎬 Basic Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import logbook

    from chameleon_log import RichHandler

    # Create a RichHandler with default settings
    handler = RichHandler()

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started successfully')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

This will produce colorful, formatted output in your terminal with proper log levels and structured tracebacks.

🖼️ Output
~~~~~~~~~~~

.. image:: https://quan-images.b-cdn.net/blogs/2026/04/rich-simple.png
   :alt: Rich Handler Output
   :width: 100%

.. image:: https://quan-images.b-cdn.net/blogs/2026/04/rich-traceback.png
   :alt: Rich Handler Output
   :width: 100%


📝 Complete Example
~~~~~~~~~~~~~~~~~~~~~

For a more complete example showing all log levels and features, see ``examples/cli-simple.py`` and ``examples/cli-rich-tracebacks.py``:

.. literalinclude:: ../examples/cli-simple.py
   :language: python

For a demo that shows Rich-formatted tracebacks, run:

.. code-block:: bash

    python examples/cli-rich-tracebacks.py

🐧 JournaldHandler
===================

.. note::

    JournaldHandler requires Linux with `systemd`_. Install with: ``pip install chameleon_log[journald]``

The :py:class:`~chameleon_log.journald.JournaldHandler` writes logs directly to `systemd`_ `journald`_ for **production/live systems**, with full metadata preservation.

🎬 Basic Usage
~~~~~~~~~~~~~~~~~

Basic :py:class:`~chameleon_log.journald.JournaldHandler` usage without extra parameters:

.. code-block:: python

    import logbook
    from chameleon_log.journald import JournaldHandler

    # Create a JournaldHandler
    handler = JournaldHandler()

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started successfully')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

View logs with ``journalctl``:

.. code-block:: shell

    journalctl -u my-service  # Or by `systemd`_ unit name
    journalctl -t my-app  # Filter by syslog identifier

📝 Simple Example
~~~~~~~~~~~~~~~~~~~

See ``examples/journald-simple.py`` for a complete basic example with exception handling:

.. literalinclude:: ../examples/journald-simple.py
   :language: python
   :lines: 1-42

This example demonstrates basic logging at different levels and exception handling without using extra fields.

.. _systemd: https://systemd.io/
.. _journald: https://wiki.archlinux.org/title/Systemd/Journal
