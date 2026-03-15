#!/usr/bin/env python3
"""Test that the logbook Processor approach works correctly."""

import logbook
from logbook import Logger, Processor
from chameleon_log import JournaldHandler

handler = JournaldHandler(syslog_identifier='processor-test')

with handler:
    log = Logger('TestApp')
    
    # Without processor - have to pass farm in every call
    log.info('Message 1', farm='tomato')
    log.info('Message 2', farm='tomato')
    
    # With processor - farm is automatically added
    def inject_context(record):
        record.extra['farm'] = 'rose'
    
    with Processor(inject_context):
        log.info('Message 3')  # farm='rose' is automatic
        log.info('Message 4')  # farm='rose' is automatic
        log.warning('Warning message')  # farm='rose' is automatic

print("✓ Test completed successfully")
print("✓ Check journalctl output to verify extra fields are set correctly")
