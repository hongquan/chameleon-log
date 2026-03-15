#!/usr/bin/env python3
"""Example of using JournaldHandler with extra fields and concurrent logging."""

import concurrent.futures
import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle

import logbook
from logbook import Logger, Processor

from chameleon_log.journald import JournaldHandler


def get_sensor_values() -> dict[str, int | float]:
    """Simulate reading sensor values."""
    return {'temperature': random.randint(25, 30), 'humidity': random.randint(80, 99)}


def pretend_to_compute_for_decision() -> None:
    """Simulate computation time."""
    time.sleep(random.randint(2, 8) / 10)


def pretend_to_run_pump() -> None:
    """Simulate pump operation."""
    time.sleep(random.randint(5, 20) / 10)


def control_farm(farm_name: str, handler: JournaldHandler) -> None:
    """Control a farm with logging using Processor to inject farm context."""
    with handler:
        log = Logger(f'{farm_name}-farm')
        
        # Use a Processor to inject farm name into all log records in this context.
        # This avoids having to pass farm=farm_name in every log call.
        def inject_farm_context(record: logbook.LogRecord) -> None:
            record.extra['farm'] = farm_name
        
        with Processor(inject_farm_context):
            sensors = get_sensor_values()
            # Extra fields can still be added per-call
            log.debug('Sensor values: {}', sensors, sensor_type='environment')
            pretend_to_compute_for_decision()
            log.warning('Farm {} is too hot', farm_name, alert_type='temperature')
            log.info('Turn pump on...', action='pump_start')
            pretend_to_run_pump()
            log.info('Turn pump off.', action='pump_stop')


def control_farm_with_extra_fields(farm_name: str, handler: JournaldHandler) -> None:
    """Control a farm with extra fields using a different approach."""
    with handler:
        log = Logger(f'{farm_name}-farm')
        
        # Example: Use extra= parameter for one-off extra fields
        # This is simpler than a Processor when you only need fields for a single log call
        sensors = get_sensor_values()
        log.debug(
            'Sensor values: {}',
            sensors,
            extra={
                'farm': farm_name,
                'sensor_type': 'environment',
                'crop': 'mixed'
            }
        )
        
        pretend_to_compute_for_decision()
        
        # Example: Use Processor for context that applies to multiple calls
        def inject_alert_context(record: logbook.LogRecord) -> None:
            record.extra['farm'] = farm_name
            record.extra['alert_type'] = 'temperature'
            record.extra['severity'] = 'medium'
        
        with Processor(inject_alert_context):
            log.warning('Farm {} is too hot', farm_name)
            log.info('Turn pump on...', action='pump_start', duration='short')
            pretend_to_run_pump()
            log.info('Turn pump off.', action='pump_stop', status='completed')


def main() -> None:
    """Main function demonstrating JournaldHandler with extra fields."""
    # Create a JournaldHandler with custom prefix for extra fields
    handler = JournaldHandler(
        syslog_identifier='farm-controller',
        extra_field_prefix='F_'  # This is the default, but shown here for clarity
    )
    
    # Example 1: Simple logging with extra fields using extra= parameter
    with handler:
        logger = Logger('FarmApp')
        logger.info(
            'Starting farm control system',
            extra={'app_version': '1.0.0', 'region': 'southeast'}
        )
    
    # Example 2: Control multiple farms concurrently to show interleaved logs
    farms = ('tomato', 'rose', 'mushroom', 'corn')
    jobs = []
    
    # Alternate between the two control functions to demonstrate different approaches
    with ThreadPoolExecutor(max_workers=2) as executor:
        for flag, farm in zip(cycle((False, True)), farms):
            func = control_farm_with_extra_fields if flag else control_farm
            future = executor.submit(func, farm, handler)
            jobs.append(future)
    
    # Wait for all farms to complete
    concurrent.futures.wait(jobs)
    
    # Log completion
    with handler:
        logger = Logger('FarmApp')
        logger.info(
            'All farm operations completed',
            extra={'status': 'success', 'farms_controlled': len(farms)}
        )


if __name__ == '__main__':
    main()
