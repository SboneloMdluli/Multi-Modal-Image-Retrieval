import functools
import time

import logging_config

logger = logging_config.logger


def timing_decorator(func):
    """Decorator to measure and log function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Completed {func.__name__} (took: {duration:.2f} seconds)")
        return result

    return wrapper
