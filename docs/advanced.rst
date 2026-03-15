Advanced Usage
==============

JournaldHandler (optional)
--------------------------

The :py:class:`~chameleon_log.journald.JournaldHandler` is only available when the ``journald`` extra is installed:

.. code-block:: bash

   pip install chameleon_log[journald]

.. note::

   The ``journald`` extra requires Linux with systemd and installs the ``systemd-python`` package.

Extra Fields with JournaldHandler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One advantage of using *journald* is that we can attach extra info to each log entry and filter by that info.
One example is in multi-tenant systems where logs from many tenants mix together, making it difficult to debug
for a particular tenant. With *journald* we can attach tenant ID and filter logs by that tenant ID.

Logbook provides two ways to attach extra data to log records:

**Option 1: Use the extra= parameter (simple and direct)**

Best for adding fields to a single log call:

.. code-block:: python

   logger.info('User action', extra={'user_id': 123, 'action': 'login'})
   # Results in fields: F_USER_ID=123, F_ACTION=login

**Option 2: Use a Processor (for reusable context)**

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

When using ``JournaldHandler``, extra fields from ``record.extra`` are sent to journald. These fields are:

.. literalinclude:: ../examples/journald-extra-fields.py
   :language: python

When viewing logs with ``journalctl``, we can filter with ``F_FARM`` option:

.. code-block:: shell

   journalctl -u farm-controller F_FARM=tomato

RichHandler Configuration
-------------------------

The :py:class:`~chameleon_log.rich.RichHandler` provides Rich-based colourful output for Logbook. You can customize its behavior:

.. code-block:: python

   import logbook
   from chameleon_log import RichHandler
   
   handler = RichHandler(
       level=logbook.DEBUG,
       enable_link_path=True,
       force_terminal=True
   )
   
   with handler:
       logger = logbook.Logger('MyApp')
       logger.info('Application started')

The handler supports all Logbook log levels and provides formatted exception tracebacks with syntax highlighting.

See the examples directory for more detailed usage patterns.

Automatic Handler Selection
---------------------------

You can use :py:func:`~chameleon_log.is_connected_journald` to automatically select the appropriate handler based on the runtime environment:

.. code-block:: python

   from chameleon_log import is_connected_journald, RichHandler
   from chameleon_log.journald import JournaldHandler
   
   if is_connected_journald():
       # Production: systemd service - use journald
       handler = JournaldHandler(syslog_identifier='my-service')
   else:
       # Development: terminal - use pretty console output
       handler = RichHandler()
   
   with handler:
       logger.info('Application started')

This allows the same codebase to work seamlessly in both development and production environments. See ``examples/auto-detect-handler.py`` for a complete example.
