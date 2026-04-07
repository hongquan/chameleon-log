from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import logbook

from chameleon_log import RichHandler


def do_some_failed_action() -> None:
    msg = 'Something went wrong!'
    raise ValueError(msg)


def main() -> None:
    handler = RichHandler(rich_tracebacks=True)

    with handler:
        logger = logbook.Logger(__name__)

        logger.debug('This is a debug message')
        logger.info('Application started successfully')
        logger.notice('This is a notice message')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

        birthday = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).replace(
            hour=20, minute=0, second=0, microsecond=0
        ) - timedelta(20 * 365)
        user_data = {'id': 123, 'name': 'Lê Lợi', 'active': True, 'birthday': birthday}
        logger.info('User logged in: {}', user_data)

        logger.info(
            '127.0.0.1 - - [15/Mar/2026:17:30:45 +0700] "GET /api/v1/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
        )

        try:
            do_some_failed_action()
        except ValueError:
            logger.exception('An error occurred during processing')


if __name__ == '__main__':
    main()
