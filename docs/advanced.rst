🛠️ Advanced Usage
===================

🐧 JournaldHandler
------------------

The :py:class:`~chameleon_log.journald.JournaldHandler` is only available when the ``journald`` extra is installed:

.. code-block:: bash

    pip install chameleon-log[journald]
    # or with uv:
    uv add chameleon-log --extra journald

.. note::

    The ``journald`` extra requires Linux with systemd and installs the ``journald-send`` package.

`journald`_ lets you attach structured metadata to log messages, enabling powerful filtering.
This is especially useful in multi-tenant systems where logs from many tenants mix together.

`Logbook`_ provides two ways to attach extra fields to log records:

*Option 1*: Use the ``extra=`` parameter (simple and direct)

.. code-block:: python

    logger.info('User action', extra={'user_id': 123, 'action': 'login'})
    # Results in fields: F_USER_ID=123, F_ACTION=login in `journald`_

*Option 2*: Use a ``Processor`` (for reusable context)

.. code-block:: python

    from logbook import Logger, Processor

    def inject_request_context(record):
        record.extra['request_id'] = 'abc-123'
        record.extra['user_id'] = 456

    with Processor(inject_request_context):
        logger.info('Processing started')
        logger.info('Processing completed')
        # Both logs will have F_REQUEST_ID and F_USER_ID fields

See ``examples/journald-extra-fields.py`` for a runnable example:

.. literalinclude:: ../examples/journald-extra-fields.py
   :language: python

✨ RichHandler configuration
----------------------------

The ``RichHandler`` can be customized with ``level``, ``console``, ``rich_tracebacks``, and other parameters:

.. code-block:: python

    import logbook
    from chameleon_log import RichHandler

    handler = RichHandler(
        level=logbook.DEBUG,         # Set minimum log level
        console=True,                # Auto-detect terminal / force plain / pass a Console
        rich_tracebacks=True,        # Editor-like tracebacks
    )

The ``console`` parameter controls Rich rendering:

- ``True`` (default): Auto-detect based on ``isatty()``.
- ``False``: Render plain output.
- A ``rich.Console`` instance: Use that Console directly (e.g. with a ``rich.progress.Progress`` live display).

🤖 Conditional handler selection
--------------------------------

Select the appropriate handler based on the environment:

.. code-block:: python

    from chameleon_log import is_connected_journald, RichHandler
    from chameleon_log.journald import JournaldHandler

    if is_connected_journald():
        handler = JournaldHandler(syslog_identifier='my-service')
    else:
        handler = RichHandler()

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started')

Quick handler selection with get_log_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a more concise approach, use :py:func:`~chameleon_log.detectors.get_log_handler`:

.. code-block:: python

    from chameleon_log import get_log_handler

    handler = get_log_handler(syslog_identifier='my-service')

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started')

See ``examples/auto-detect-handler.py`` for a complete working example:

.. literalinclude:: ../examples/auto-detect-handler.py
   :language: python

🐧 Viewing logs with journalctl
-------------------------------

When using :py:class:`~chameleon_log.journald.JournaldHandler`, view and filter logs with ``journalctl``:

.. code-block:: shell

    journalctl -fu my-service
    journalctl -t my-app
    journalctl -t my-app F_USER_ID=123
    journalctl -eu my-service -o json

The ``syslog_identifier`` is helpful when your app runs across multiple systemd units, allowing you to use ``journalctl -t`` to view all logs from your application.

🔴 SentryHandler
-----------------

The :py:class:`~chameleon_log.sentry.SentryHandler` forwards Logbook records to `Sentry`_ for error tracking and monitoring.
Install it with the ``sentry`` extra:

.. code-block:: bash

    pip install chameleon-log[sentry]
    # or with uv:
    uv add chameleon-log --extra sentry

Initialize Sentry and attach the handler:

.. code-block:: python

    import logbook
    import sentry_sdk
    from chameleon_log.sentry import SentryHandler

    sentry_sdk.init(dsn='https://...@sentry.io/123')
    logger = logbook.Logger('myapp')
    handler = SentryHandler(level=logbook.ERROR)

    with handler:
        logger.error('Database connection failed')

Exception-aware forwarding
~~~~~~~~~~~~~~~~~~~~~~~~~~

When a record carries an exception (:exc:`exc_info=True`), the event is sent with a stacktrace.
Plain records (no exception) become events with the formatted message, channel, and ``extra`` fields attached.

Combined with journald
~~~~~~~~~~~~~~~~~~~~~~

Use ``SentryHandler`` alongside ``JournaldHandler`` — filter ``SentryHandler`` to WARNING+ so only meaningful events reach Sentry while local logs stay verbose:

.. code-block:: python

    from chameleon_log import RichHandler
    from chameleon_log.journald import JournaldHandler
    from chameleon_log.sentry import SentryHandler

    handlers = [
        RichHandler(),
        journald_handler := JournaldHandler(syslog_identifier='my-service'),
        SentryHandler(level=logbook.WARNING),  # Only warnings and above go to Sentry
    ]

    with *handlers:
        ...

.. figure:: https://quan-images.b-cdn.net/blogs/2026/08/logbook-sentry.png
   :alt: Sentry dashboard showing multiple events captured from Logbook records

   Multiple events captured by ``SentryHandler`` as shown in the Sentry dashboard

.. _journald: https://wiki.archlinux.org/title/Systemd/Journal
.. _Logbook: https://pypi.org/project/Logbook/
.. _Sentry: https://docs.sentry.io/
