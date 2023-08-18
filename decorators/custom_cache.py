import logging
from functools import wraps
from django.core.cache import cache
from django.utils.cache import patch_response_headers
from asgiref.sync import sync_to_async


def custom_cache_page(timeout: int,
                      cache_key_func=None, cache_status_codes: list = [200]):

    """
    Custom cache decorator for Django views.

    Args:
        timeout (int): The cache timeout in seconds.
        cache_key_func (function, optional): A function that generates
            the cache key. Defaults to None.
        cache_status_codes (list, optional): List of status codes
            that should be cached. Defaults to [200].

    Returns:
        function: A decorator that applies caching to a view function.

    Usage:
        Apply this decorator to a view function that needs caching.

    Example:
        @custom_cache_page(timeout=3600,
                           cache_key_func=my_cache_key_func)
        async def my_view(request):
            # Your view logic here

    """
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped_view(request, *args, **kwargs):
            cache_key = request.build_absolute_uri()
            if cache_key_func:
                cache_key = await sync_to_async(
                    cache_key_func)(request, *args, **kwargs)
                if cache_key is None:
                    cache_key = None

            response = await sync_to_async(
                cache.get)(cache_key) if cache_key else None

            if response is None:
                response = await view_func(request, *args, **kwargs)
                logging.error(f'response{response}')
                if response.status_code in cache_status_codes:
                    patch_response_headers(response, timeout)
                    if hasattr(response, 'render') and callable(response.render):
                        async def set_cache(val, cache_key):
                            if cache_key:
                                await sync_to_async(cache.set)(cache_key, val, timeout)
                        response.add_post_render_callback(lambda val: set_cache(val, cache_key))
                    else:
                        if cache_key:
                            await sync_to_async(cache.set)(cache_key, response, timeout)
            return response
        return _wrapped_view
    return decorator
