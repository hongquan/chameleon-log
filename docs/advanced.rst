🛠️ Advanced Usage
===================

🐧 JournaldHandler
------------------

For applications deployed on Linux servers, writing logs directly to systemd `journald`_, using its protocol, (rather than files or *stdout*/*stderr*) provides more efficient troubleshooting with filterable metadata.

Using `journald`_ protocol (with :py:class:`~chameleon_log.journald.JournaldHandler`) is not the same as writing logs to *stdout*/*stderr* and letting `journald`_ collect them. The latter loses important metadata (timestamps, severity levels, extra fields) that enable powerful filtering.

The :py:class:`~chameleon_log.journald.JournaldHandler` is only available when the ``journald`` extra is installed:

.. code-block:: bash

    pip install chameleon_log[journald]
    # or with uv:
    uv add chameleon_log --extra journald

.. note::

    The ``journald`` extra requires Linux with systemd and installs the ``systemd-python`` package.

Other than storing logs as structured data, preserve the context around a log message, `journald`_ also allows to attach metadata to enable powerful filtering.
This is especially useful in multi-tenant systems where logs from many tenants mix together.


`Logbook`_ provides two ways to attach extra fields to log records:

*Option 1*: Use the ``extra=`` parameter (simple and direct)

Best for adding fields to a single log call:

.. code-block:: python

    logger.info('User action', extra={'user_id': 123, 'action': 'login'})
    # Results in fields: F_USER_ID=123, F_ACTION=login in `journald`_

*Option 2*: Use a ``Processor`` (for reusable context)

Best for injecting context into multiple log calls:

.. code-block:: python

    from logbook import Logger, Processor

    def inject_request_context(record):
        record.extra['request_id'] = 'abc-123'
        record.extra['user_id'] = 456

    with Processor(inject_request_context):
        logger.info('Processing started')
        logger.info('Processing completed')
        # Both logs will have F_REQUEST_ID and F_USER_ID fields


The following example demonstrates logging from multiple concurrent farms, each with its own context:

.. literalinclude:: ../examples/journald-extra-fields.py
   :language: python


✨ RichHandler configuration
----------------------------

The ``RichHandler`` can be customized for different use cases:

.. code-block:: python

    import logbook
    from chameleon_log import RichHandler

    handler = RichHandler(
        level=logbook.DEBUG,           # Set minimum log level
        enable_link_path=True,         # Enable clickable file paths in terminals
        rich_rendering=True            # Always use Rich colorful rendering
    )

    with handler:
        logger = logbook.Logger(__name__)
        logger.debug('Debug information')
        logger.info('Application started')

The handler supports all `Logbook`_ log levels and provides formatted exception tracebacks with syntax highlighting.

Sometimes, the application's ``stderr`` is connected to something not a Terminal, so it does not make sense to render the colors, table layout.
The ``rich_rendering`` parameter allows you to disable / enable that feature:

- ``True``: Always use Rich colorful rendering.
- ``False``: Disable Rich formatting, render plain output.
- ``None`` (default): Auto-detect based on ``isatty()``.

Additionally, the handler exposes a ``rich_tracebacks`` flag to control how exceptions are displayed:

- ``rich_tracebacks=True``: The traceback is rendered with editor-like interface: line numbers and frames.
- ``rich_tracebacks=False`` (default): Simple display of traceback, like it is done originally with Python, with colors added.

Example enabling rich tracebacks::

    from chameleon_log import RichHandler

    handler = RichHandler(rich_tracebacks=True, rich_rendering=True)

See the examples in the ``examples/`` directory for runnable demos that show both behaviors.

🤖 Conditional handler selection
--------------------------------

Each handler is only suitable for a running environment, you can implement the feature to conditionally switch to the appropriate handler with the help of ``is_connected_journald``.


.. code-block:: python

    from chameleon_log import is_connected_journald, RichHandler
    from chameleon_log.journald import JournaldHandler

    if is_connected_journald():
        # Production: systemd service - use `journald`_
        handler = JournaldHandler(syslog_identifier='my-service')
    else:
        # Development: terminal - use pretty console output
        handler = RichHandler()

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started')


Complete auto-detection example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See ``examples/auto-detect-handler.py`` for a complete working example:

.. literalinclude:: ../examples/auto-detect-handler.py
   :language: python

🐧 Viewing logs with journalctl
-------------------------------

When using :py:class:`~chameleon_log.journald.JournaldHandler`, logs can be viewed and filtered using ``journalctl``:

.. code-block:: shell

    # Follow logs for a systemd service
    journalctl -fu my-service

    # Filter by syslog identifier
    journalctl -t my-app

    # Filter by custom fields
    journalctl -t my-app F_USER_ID=123

    # Output as JSON for structured analysis
    journalctl -eu my-service -o json

Normally, you view app logs with ``-u`` (unit name). The ``syslog_identifier`` is helpful when your app runs across multiple systemd units, allowing you to use ``journalctl -t`` to view all logs from your application.

.. _journald: https://wiki.archlinux.org/title/Systemd/Journal
.. _Logbook: https://pypi.org/project/Logbook/
