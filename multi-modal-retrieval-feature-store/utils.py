import functools
import time

import logging_config

logger = logging_config.logger


def timing_decorator(func):
    """Decorator to measure and log function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Starting %s", func.__name__)
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            "%s completed in %.2f seconds", func.__name__, end_time - start_time
        )
        return result

    return wrapper
