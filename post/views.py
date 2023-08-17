import logging
import dask
import json
import dask.multiprocessing
import asyncio

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import (
	transaction, 
	IntegrityError, 
	DatabaseError
)

from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.request import Request

from exceptions.error_codes import ErrorCodes
from exceptions.service_error import ServiceException

from .async_queries import (
	retry_update_post, 
	get_post_async, 
	post_exists_async, 
	post_create_async, 
	update_post_sync
)

from decorators.custom_cache import custom_cache_page
from utils.response import SendAsyncResponse
from utils.common import validate_analyzed_data_response
from utils.caching_functions import (
	analyze_post_cache_key_function, 
	create_post_cache_key_function
)

from .models import Post  # Import your Comment model
from .serializers import PostValidationSerializer  # Import your Comment serializer
from .tasks import analyze_post
from .core import divide_text, analyze_text, process_subtext_results



@custom_cache_page(60*1, cache_key_func=create_post_cache_key_function, cache_status_codes=[409])
async def create_post(request, *args, **kwargs):
	"""
	Create A new Post.

	:param request: The HTTP request object.
	:param args: Additional positional arguments.
	:param kwargs: Additional keyword arguments.
	:return: Response containing the created post_id details.
	
	:request body: {
			'uuid': "550e8400-e29b-41d4-a716-446655440008",
			'text': "This is sample string"
		}
	:response:{
	"status": 201,
	"data": {
	"uuid": "550e8400-e29b-41d4-a716-446655440008"
	},
	"message": "Post Created Successfully",
	"error_code": null
		}
	"""

	try:
		if request.method != 'POST':
			raise ServiceException(
				status.HTTP_405_METHOD_NOT_ALLOWED, 
				ErrorCodes.METHOD_NOT_ALLOWED, 
				message=f'Method not allowed')
	
		response_dict = dict()
		serializer = PostValidationSerializer(data=json.loads(request.body))
		if serializer.is_valid():
		
			valid_data = serializer.validated_data

			uuid = valid_data['uuid']
			existing_post = await post_exists_async(uuid)

			if existing_post:
				raise ServiceException(
					status.HTTP_409_CONFLICT, ErrorCodes.RESOURCE_DUPLICATION, 
					f'Unique Id {uuid} already Exist in the system')

			post = await post_create_async(valid_data)
			response_dict['uuid'] = post.uuid

			
			return SendAsyncResponse(
				status.HTTP_201_CREATED, response_dict, f'Post Created Successfully')
		
		raise ServiceException(
			status.HTTP_400_BAD_REQUEST, 
			ErrorCodes.REQUEST_VALIDATION_FAILED, 'Invalid post data')
	
	except ServiceException as e:
		return SendAsyncResponse(
			e.status_code, None, 
			error_code=e.error_code, message=e.message)
	
	except Exception as e:
			return SendAsyncResponse(
				status.HTTP_500_INTERNAL_SERVER_ERROR, None, 
				error_code=500, message=str(e))



@custom_cache_page(60*1, cache_key_func=analyze_post_cache_key_function)
async def get_post_analysis(request: Request, post_id: str, *args: list, **kwargs: dict) -> dict:
	"""
	Retrieve and return the analysis details of a specific post.

	:param request: The HTTP request object.
	:param post_id: The unique identifier of the post.
	:param args: Additional positional arguments.
	:param kwargs: Additional keyword arguments.
	:return: Response containing the analysis details.
	:response:{
	"status": 200,
	"data": {
		"post_id": "550e8400-e29b-41d4-a716-446655440000",
		"is_analysed": false,
		"analysis": {
					'total_words': 5,
					'average_word_length': 6
		}
	},
	"message": "Fetched analysis successfully",
	"error_code": null
	}
	"""
	try:
			
		response_dict = dict()
		text_parts = []
		post = await get_post_async(post_id)

		logging.error(f'{post.is_analysed}')
		
		if post.is_analysed:
			logging.error("hererer")
			response_dict = {
				"post_id": post.uuid,
		"is_analysed": post.is_analysed,
		"analysis": post.analysis_response
		},
			return SendAsyncResponse(status.HTTP_200_OK, 
				response_dict, message='Fetched analysis successfully')
		
		text = post.post_description
		text_part_generator = divide_text(text,10)
		
		with dask.config.set(scheduler='processes'):
			results_dask = dask.compute(
				*[dask.delayed(analyze_text)(part) for _, part in enumerate(text_part_generator)])

		analyzed_data = process_subtext_results(results_dask)
		
		logging.error(f'analyzed_data{analyzed_data}')
		is_valid_analysis = validate_analyzed_data_response(analyzed_data)
		if not is_valid_analysis:
			raise ServiceException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
				ErrorCodes.RESPONSE_DATA_NOT_CORRECT, f'Unexpected analysis data')
		
		response_dict['post_id'] = post_id
		response_dict['is_analysed'] = 'Hello'
		response_dict['analysis'] = analyzed_data
		
		await update_post_sync(post_id, analyzed_data)

		return SendAsyncResponse(
			status.HTTP_200_OK, response_dict, message='Fetched analysis successfully')

	except ValidationError:
		raise ServiceException(status.HTTP_400_BAD_REQUEST, 
			ErrorCodes.REQUEST_VALIDATION_FAILED, f'Not a valid post id')

	except ServiceException as e:
		return SendAsyncResponse(
			e.status_code, None, error_code=e.error_code, message=e.message)

	except Exception as e:
		return SendAsyncResponse(
		status.HTTP_500_INTERNAL_SERVER_ERROR, None, 
		error_code=500, message=str(e))

	
	 





