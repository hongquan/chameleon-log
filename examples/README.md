# ChameleonLog Examples

This directory contains examples demonstrating how to use ChameleonLog with different handlers.

## Examples Overview

### Basic Examples

- **cli-simple.py** - Basic example using RichHandler for colorful console output
  ```bash
  python cli-simple.py
  ```

- **cli-rich-tracebacks.py** - Basic example using RichHandler with rich tracebacks enabled
  ```bash
  python cli-rich-tracebacks.py
  ```

### Journald Examples

These examples demonstrate using JournaldHandler to send logs to systemd journal.

**Note**: These examples require Linux with systemd and the `journald-send` package installed.

#### journald-simple.py

A simple example showing basic logging to journald with extra fields:

```bash
sudo python journald-simple.py
```

View the logs:
```bash
journalctl -t chameleon-log-example -o json
# or
journalctl -t chameleon-log-example --output=verbose
```

Filter by extra fields:
```bash
journalctl -t chameleon-log-example F_PLATFORM=<value>
journalctl -t chameleon-log-example F_ERROR_TYPE=conversion
```

#### journald-extra-fields.py

An advanced example demonstrating:
- Multiple concurrent loggers
- Rich extra fields with custom prefixes
- Filtering and querying logs by fields

```bash
sudo python journald-extra-fields.py
```

View and filter logs:
```bash
# View all logs from the farm controller
journalctl -t farm-controller

# Filter by farm name
journalctl -t farm-controller F_FARM=tomato

# Filter by action type
journalctl -t farm-controller F_ACTION=pump_start

# Filter by alert type
journalctl -t farm-controller F_ALERT_TYPE=temperature

# Show JSON output for structured viewing
journalctl -t farm-controller -o json | jq .
```

### Sentry Examples

These examples demonstrate using SentryHandler to forward Logbook records to Sentry.

**Note**: These examples require the `sentry-sdk` package. Install it with:

```bash
pip install sentry-sdk
# or
pip install chameleon_log[sentry]
```

#### sentry-simple.py

A simple example showing basic logging forwarded to Sentry, including:

- Different log levels (notice and trace are normalized to `info` and `debug`)
- Extra fields via `extra=` and via a `Processor`
- Exception capture with stacktraces

When `SENTRY_DSN` is set the events are sent to your Sentry project. Without
it the events are dropped via `before_send` after each one is pretty-printed
to stdout, so the example is runnable without a Sentry account:

```bash
python sentry-simple.py

# Or, to actually send the events somewhere:
SENTRY_DSN=https://...@o0.ingest.sentry.io/0 python sentry-simple.py
```

### Combined Examples

#### journald-sentry-combined.py

Demonstrates the typical production setup: persist structured logs to
journald (for operators to query with `journalctl`) while forwarding
errors to Sentry. Both handlers are pushed onto Logbook's stacked handler
at once, so a single `logger.error(...)` call ends up in both destinations.
`RichHandler` is normally enough during development, but in production you
usually want both of these so logs survive across restarts and the team
gets alerted on failures.

Requires Linux with systemd plus the `journald-send` and `sentry-sdk`
packages. `sudo` is optional — either run as root to write to the system
journal, or run as a user unit (`systemctl --user`) to write to the user
journal:

```bash
python journald-sentry-combined.py

# Or, to actually send the events somewhere:
SENTRY_DSN=https://...@o0.ingest.sentry.io/0 python journald-sentry-combined.py
```

View the user journal side:

```bash
journalctl --user -t chameleon-log-combined -f
```

View the system journal side (when run with `sudo`):

```bash
journalctl -t chameleon-log-combined -f
```

### Installation for Journald Examples

The journald examples require the `journald-send` package. Install it with:

```bash
pip install journald-send
# or
pip install chameleon_log[journald]
```

### Key Concepts

#### Extra Fields

Logbook provides two ways to attach extra data to log records:

**Option 1: Use the `extra=` parameter (simple and direct)**

Best for adding fields to a single log call:

```python
logger.info('User action', extra={'user_id': 123, 'action': 'login'})
# Results in fields: F_USER_ID=123, F_ACTION=login
```

**Option 2: Use a `Processor` (for reusable context)**

Best for injecting context into multiple log calls:

```python
from logbook import Logger, Processor

def inject_request_context(record):
    record.extra['request_id'] = 'abc-123'
    record.extra['user_id'] = 456

with Processor(inject_request_context):
    logger.info('Processing started')
    logger.info('Processing completed')
    # Both logs will have F_REQUEST_ID and F_USER_ID fields
```

When using ``JournaldHandler``, extra fields from ``record.extra`` are sent to journald. These fields are:

1. Prefixed with `extra_field_prefix` (default: `F_`)
2. Automatically uppercased by the handler
3. Queryable with `journalctl`

See the journald examples for complete usage patterns.

#### Viewing Logs

Use `journalctl` to view logs:

```bash
# By syslog identifier
journalctl -t your-identifier

# JSON output
journalctl -t your-identifier -o json

# Verbose output with all fields
journalctl -t your-identifier --output=verbose

# Filter by specific field
journalctl -t your-identifier F_FIELD_NAME=value

# Follow logs in real-time
journalctl -t your-identifier -f
```
