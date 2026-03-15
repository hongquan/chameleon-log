import os


def is_connected_journald() -> bool:
    '''
    Detect if the current process is connected to systemd journal.
    
    This function helps developers automatically select the appropriate log handler
    based on the runtime environment. The typical use case is:
    
    - **Development/Terminal**: Logs should appear in console with pretty formatting
    - **Production/Service**: Logs should go to systemd journal for structured logging
    
    Detection is based on environment variables: returns ``True`` only when
    ``JOURNAL_STREAM`` is set (indicating journald is available) AND ``TERM``
    is NOT set (indicating we're not in an interactive terminal).
    
    This enables you to write code that works seamlessly in both environments::
    
        from chameleon_log import is_connected_journald, RichHandler
        from chameleon_log.journald import JournaldHandler
        
        # Auto-select handler based on environment
        if is_connected_journald():
            # Production: structured logs in journald
            handler = JournaldHandler(syslog_identifier='my-service')
        else:
            # Development: pretty console output
            handler = RichHandler()
        
        with handler:
            log.info('Application starting')
            # ... your application code ...
    
    Returns:
        ``True`` if connected to journald (running as a service), ``False`` otherwise
    '''
    # Check if journaled environment variables indicate we're running as a service
    journal_stream = os.getenv('JOURNAL_STREAM')
    if not journal_stream:
        return False
    return not os.getenv('TERM')
