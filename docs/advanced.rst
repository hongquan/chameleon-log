🛠️ Advanced Usage
===================

📦 Installation with Optional Dependencies
===========================================

🐧 JournaldHandler
~~~~~~~~~~~~~~~~~~~
The :py:class:`~chameleon_log.journald.JournaldHandler` is only available when the ``journald`` extra is installed:

.. code-block:: bash

    pip install chameleon_log[journald]
    # or with uv:
    uv add chameleon_log --extra journald

.. note::

    The ``journald`` extra requires Linux with systemd and installs the ``systemd-python`` package.

🐧 JournaldHandler Advanced Features
====================================

For applications deployed on Linux servers, writing logs directly to systemd `journald <https://wiki.archlinux.org/title/Systemd/Journal>`_ (rather than files or stdout) provides more efficient troubleshooting with filterable metadata.

The ``JournaldHandler`` is not the same as writing logs to stdout/stderr and letting `journald <https://wiki.archlinux.org/title/Systemd/Journal>`_ collect them. The latter loses important metadata (timestamps, severity levels, extra fields) that enable powerful filtering.

🏗️ Complete Example with Extra Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following complete example demonstrates advanced ``JournaldHandler`` features including extra fields and exception handling:

.. literalinclude:: ../examples/journald-simple.py
   :language: python

🏗️ Extra Fields for Structured Filtering
==========================================

One advantage of `journald <https://wiki.archlinux.org/title/Systemd/Journal>`_ is the ability to attach structured data to log entries, enabling powerful filtering. This is especially useful in multi-tenant systems where logs from many tenants mix together.

🏗️ Two Approaches for Adding Extra Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Logbook <https://pypi.org/project/Logbook/>`_ provides two ways to attach extra fields to log records:

*Option 1*: Use the ``extra=`` parameter (simple and direct)

Best for adding fields to a single log call:

.. code-block:: python

    logger.info('User action', extra={'user_id': 123, 'action': 'login'})
    # Results in fields: F_USER_ID=123, F_ACTION=login in `journald <https://wiki.archlinux.org/title/Systemd/Journal>`_

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

🏗️ Example with Multiple Concurrent Sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example demonstrates logging from multiple concurrent farms, each with its own context:

.. literalinclude:: ../examples/journald-extra-fields.py
   :language: python

✨ RichHandler Configuration
=================================

The ``RichHandler`` can be customized for different use cases:

.. code-block:: python

    import logbook
    from chameleon_log import RichHandler

    handler = RichHandler(
        level=logbook.DEBUG,           # Set minimum log level
        enable_link_path=True,         # Enable clickable file paths in terminals
        rich_rendering=RichRendering.ON  # Always use Rich colorful rendering
    )

    with handler:
        logger = logbook.Logger(__name__)
        logger.debug('Debug information')
        logger.info('Application started')

The handler supports all `Logbook <https://pypi.org/project/Logbook/>`_ log levels and provides formatted exception tracebacks with syntax highlighting.

The ``rich_rendering`` parameter controls Rich formatting:

- ``RichRendering.ON``: Always use Rich colorful rendering
- ``RichRendering.OFF``: Disable Rich formatting, render plain output
- ``None`` (default): Auto-detect based on ``isatty()``

🤖 Automatic Handler Selection
==============================

For codebases that need to work in both development and production environments, you can automatically select the appropriate handler based on the runtime environment:

.. code-block:: python

    from chameleon_log import is_connected_journald, RichHandler
    from chameleon_log.journald import JournaldHandler

    if is_connected_journald():
        # Production: systemd service - use `journald <https://wiki.archlinux.org/title/Systemd/Journal>`_
        handler = JournaldHandler(syslog_identifier='my-service')
    else:
        # Development: terminal - use pretty console output
        handler = RichHandler()

    with handler:
        logger = logbook.Logger(__name__)
        logger.info('Application started')

This allows the same codebase to work seamlessly in both environments without code changes.

🤖 Complete Auto-Detection Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See ``examples/auto-detect-handler.py`` for a complete working example:

.. literalinclude:: ../examples/auto-detect-handler.py
   :language: python

🐧 Viewing Logs with journalctl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``JournaldHandler``, logs can be viewed and filtered using ``journalctl``:

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
