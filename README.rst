🦎 ChameleonLog
===============

.. image:: https://quan-images.b-cdn.net/blogs/2026/03/chameleon-freepik.svg
   :alt: ChameleonLog Logo
   :width: 200px

Colourful logging handlers for `Logbook`_.

.. image:: https://madewithlove.vercel.app/vn?heart=true&colorA=%23ffcd00&colorB=%23da251d
   :target: https://madewithlove.vercel.app
   :alt: Made in Vietnam

.. image:: https://img.shields.io/pypi/v/chameleon_log.svg
   :target: https://pypi.org/project/chameleon-log/
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/chameleon_log.svg
   :target: https://pypi.org/project/chameleon-log/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/l/chameleon_log.svg
   :target: https://pypi.org/project/chameleon-log/
   :alt: PyPI - License

.. image:: https://common-changelog.org/badge.svg
   :target: https://common-changelog.org/
   :alt: Common Changelog

.. image:: https://readthedocs.org/projects/chameleon-log/badge/?version=latest
   :target: https://chameleon-log.readthedocs.io
   :alt: Documentation Status


ChameleonLog provides colorful, structured logging for Python applications using the `Logbook`_.

- ``RichHandler``: Beautiful console output with syntax highlighting and tracebacks using the `Rich`_ library (recommended for *development*).
- ``JournaldHandler``: Structured logging to `systemd`_ `journald`_ with automatic level-based coloring and filtering (recommended for *production/Live systems* on Linux).


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

To use the ``JournaldHandler`` for sending logs to systemd `journald`_:

.. code-block:: bash

    pip install chameleon_log[journald]

Or using uv:

.. code-block:: bash

    uv add chameleon_log --extra journald

This will also install the `systemd-python`_ package, requiring systemd-based Linux distros.

🚀 Usage
=========

✨ RichHandler
~~~~~~~~~~~~~~~

For development and debugging in terminal environments, use ``RichHandler`` for colorful, formatted console output:

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


🖼️ Example output
==================

.. image:: https://quan-images.b-cdn.net/blogs/2026/03/rich.png
   :alt: Rich Handler Output
   :width: 100%


🐧 JournaldHandler
~~~~~~~~~~~~~~~~~~~

For applications deployed on Linux servers or in production environments, use ``JournaldHandler`` to write logs directly to journald, using its native protocol. This provides more efficient troubleshooting capabilities compared to file-based logging or *stdout* / *stderr* capture.

.. note::

    This is not the same as writing logs to *stdout* / *stderr* and letting journald collect them. The latter method makes you lose important metadata (timestamps, severity levels, extra fields) needed for effective log filtering and analysis.

Basic usage:

.. code-block:: python

    import logbook
    from chameleon_log.journald import JournaldHandler

    handler = JournaldHandler(syslog_identifier='my-app')

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started successfully')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

📝 Simple logging output:
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://quan-images.b-cdn.net/blogs/2026/03/journald-simple.png
   :alt: Journald Simple Output
   :width: 100%

🏗️ With extra fields for structured filtering:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logbook provides two ways to attach extra fields:

.. image:: https://quan-images.b-cdn.net/blogs/2026/03/journald-extra-fields.png
   :alt: Journald Extra Fields Output
   :width: 100%

*Option 1*: Use the ``extra=`` parameter (simple and direct)

.. code-block:: python

    import logbook
    from chameleon_log.journald import JournaldHandler

    handler = JournaldHandler(syslog_identifier='my-app')

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('User logged in', extra={'user_id': 123, 'action': 'login'})

*Option 2*: Use a ``Processor`` (for reusable context)

.. code-block:: python

    import logbook
    from logbook import Logger, Processor
    from chameleon_log.journald import JournaldHandler

    handler = JournaldHandler()
	# or
    handler = JournaldHandler(syslog_identifier='my-app')

    # Use a Processor to inject context into multiple log records
    def inject_request_context(record):
        record.extra['user_id'] = 123
        record.extra['request_id'] = 'abc-456'

    with handler:
        logger = logbook.Logger(__name__)

        with Processor(inject_request_context):
            logger.info('User logged in')  # Fields injected automatically
            logger.info('Data processed')

View logs with ``journalctl``:

.. code-block:: bash

    journalctl -fu my-service
    journalctl -t my-app F_USER_ID=123
    journalctl -eu my-service -o json

Normally, you view your app logs with ``-u`` (*unit*), the ``syslog_identifier`` is helpful if your app
scatters across many systemd units, you then can use ``journalctl -t`` to view all.

📖 Documentation
=================

Full documentation is available at: https://chameleon-log.readthedocs.io

📄 License
==========

This project is licensed under the Apache License 2.0 - see the `LICENSE`_ file for details.

Logo by `Freepik <https://www.freepik.com>`_.

.. _logbook: https://pypi.org/project/Logbook/
.. _Rich: https://pypi.org/project/rich/
.. _systemd: https://systemd.io/
.. _journald: https://wiki.archlinux.org/title/Systemd/Journal
.. _systemd-python: https://pypi.org/project/systemd-python/
.. _LICENSE: https://github.com/hongquan/chameleon-log/blob/master/LICENSE
