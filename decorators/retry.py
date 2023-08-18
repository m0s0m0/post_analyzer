import asyncio
from retrying import retry
from rest_framework import status

from exceptions.service_error import ServiceException
from exceptions.error_codes import ErrorCodes


def async_retry_and_timeout(retries=3, wait_time=1000, timeout=10):
    """
    Decorator to add retry and timeout behavior to an asynchronous function.
    Args:
        retries (int): Number of retry attempts.
        wait_time (int): Interval between retries in milliseconds.
        timeout (int): Timeout duration in seconds.
    """

    def decorator(async_func):

        @retry(stop_max_attempt_number=retries, wait_fixed=wait_time)
        async def async_func_with_retry(*args, **kwargs):
            try:
                return await asyncio.wait_for(async_func(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                raise ServiceException(
                    status.HTTP_504_GATEWAY_TIMEOUT, ErrorCodes.GATEWAY_TIMEOUT, 'Operation timed out')

        return async_func_with_retry

    return decorator
