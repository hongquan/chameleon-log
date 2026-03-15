import logbook

from chameleon_log import RichHandler


def do_some_failed_action() -> None:
    msg = 'Something went wrong!'
    raise ValueError(msg)


def main() -> None:
    # Create a RichHandler with default settings
    handler = RichHandler()

    # Or customize the handler
    # handler = RichHandler(level=logbook.DEBUG)

    with handler:
        # Get a logger
        logger = logbook.Logger('MyApp')

        # Log messages at different levels
        logger.debug('This is a debug message')
        logger.info('Application started successfully')
        logger.notice('This is a notice message')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

        # Log with structured data
        user_data = {'id': 123, 'name': 'John Doe', 'active': True}
        logger.info('User logged in: {}', user_data)

        # Log an exception
        try:
            do_some_failed_action()
        except ValueError:
            logger.exception('An error occurred during processing')


if __name__ == '__main__':
    main()
