============
ChameleonLog
============

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


ChameleonLog provides colorful, structured logging for Python applications using the `Logbook`_ framework.

- ``RichHandler``: Beautiful console output with syntax highlighting and tracebacks using the `Rich`_ library.
- ``JournaldHandler``: Structured logging to systemd journal with automatic level-based coloring and filtering.


Installation
------------

Install ChameleonLog using pip:

.. code-block:: bash

    pip install chameleon_log

Or using uv:

.. code-block:: bash

    uv add chameleon_log

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

To use the ``JournaldHandler`` for sending logs to systemd journal (Linux only):

.. code-block:: bash

    pip install chameleon_log[journald]

Or using uv:

.. code-block:: bash

    uv add chameleon_log --extra journald

This requires Linux with systemd and installs the ``systemd-python`` package.

Usage
-----

Basic usage:

.. code-block:: python

    import logbook
    
    from chameleon_log import RichHandler

    # Create a RichHandler with default settings
    handler = RichHandler()

    with handler:
        logger = logbook.Logger('MyApp')
        logger.info('Application started successfully')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

Customizing the handler:

.. code-block:: python

    # Create a RichHandler with custom settings
    handler = RichHandler(
        level=logbook.DEBUG,
        # Additional Rich-specific options can be added here
    )

Example Output
--------------

.. code-block:: text

    [12:00:00] INFO     MyApp: Application started successfully    cli-app.py:24
               WARNING  MyApp: This is a warning message           cli-app.py:25
               ERROR    MyApp: An error occurred                   cli-app.py:26

JournaldHandler Usage
---------------------

For systemd journal integration (Linux only) via journald, use ``JournaldHandler``. Logbook provides two ways to attach extra fields:

**Option 1: Use the extra= parameter (simple and direct)**

.. code-block:: python

    import logbook
    from chameleon_log.journald import JournaldHandler

    handler = JournaldHandler(syslog_identifier='my-app')

    with handler:
        logger = logbook.Logger('MyApp')
        logger.info('User logged in', extra={'user_id': 123, 'action': 'login'})

**Option 2: Use a Processor (for reusable context)**

.. code-block:: python

    import logbook
    from logbook import Logger, Processor
    from chameleon_log.journald import JournaldHandler

    handler = JournaldHandler(syslog_identifier='my-app')

    # Use a Processor to inject context into multiple log records
    def inject_request_context(record):
        record.extra['user_id'] = 123
        record.extra['request_id'] = 'abc-456'

    with handler:
        logger = logbook.Logger('MyApp')
        
        with Processor(inject_request_context):
            logger.info('User logged in')  # Fields injected automatically
            logger.info('Data processed')

View logs with journalctl:

.. code-block:: bash

    journalctl -t my-app
    journalctl -t my-app F_USER_ID=123
    journalctl -t my-app -o json

License
-------

This project is licensed under the Apache License 2.0 - see the `LICENSE`_ file for details.

.. _logbook: https://pypi.org/project/Logbook/
.. _Rich: https://pypi.org/project/rich/
.. _systemd: https://systemd.io/
.. _journald: https://systemd.io/
.. _LICENSE: https://github.com/hongquan/chameleon-log/blob/master/LICENSE
