import json
from rest_framework.request import Request


def create_post_cache_key_function(request: Request, *args: list, **kwargs: dict) -> str:
	"""
	Custom cache key function to generate cache key based on post_id.

	:param request: The HTTP request object.
	:param args: Additional positional arguments.
	:param kwargs: Additional keyword arguments.
	:return: The cache key string.
	"""
	body = json.loads(request.body)
	uuid = body.get('uuid')
	return f'created_post_{uuid}'


def analyze_post_cache_key_function(request: Request, *args: list, **kwargs: dict) -> str:
	"""
	Custom cache key function to generate cache key based on post_id.

	:param request: The HTTP request object.
	:param args: Additional positional arguments.
	:param kwargs: Additional keyword arguments.
	:return: The cache key string.
	"""
	return f'post_analysis_{kwargs.get("post_id")}'