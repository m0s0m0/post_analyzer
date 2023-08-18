import asyncio
import logging
import datetime
from asgiref.sync import sync_to_async
from rest_framework import status

from django.db import (
    OperationalError,
    DatabaseError,
    DataError,
    InternalError,
    IntegrityError,
    transaction)

from django.core.exceptions import (
    ValidationError,
    FieldError,
    ObjectDoesNotExist,
    MultipleObjectsReturned)

from decorators.retry import async_retry_and_timeout
from exceptions.service_error import ServiceException
from exceptions.error_codes import ErrorCodes
from .models import Post


@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def get_post_async(post_id: str) -> Post:
    """
    Asynchronously retrieve a Post object based on its UUID.
    Args:
        post_id (str): The UUID of the post.
    Returns:
        Post: The retrieved Post object.
    Raises:
        ObjectDoesNotExist: If the post with the specified UUID does not exist.
    """
    try:
        post = Post.objects.get(uuid=post_id)
        return post

    except ObjectDoesNotExist:
        raise ServiceException(
            status.HTTP_404_NOT_FOUND, ErrorCodes.POST_NOT_FOUND, f'Post does not exist {post_id}')

    except MultipleObjectsReturned:
        raise ServiceException(
            status.HTTP_409_CONFLICT, ErrorCodes.MULTIPLE_POSTS_RETURNED, f'Multiple posts found for {post_id}')

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unabe to query DB')


@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def post_exists_async(post_id: str) -> Post:
    """
    Asynchronously retrieve a Post object based on its UUID.
    Args:
        post_id (str): The UUID of the post.
    Returns:
        Post: The retrieved Post object.
    Raises:
        ObjectDoesNotExist: If the post with the specified UUID does not exist.
    """
    try:
        post = Post.objects.filter(uuid=post_id).first()
        return post

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unable to query DB')


@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def post_create_async(post_data: dict) -> Post:
    """
    Asynchronously retrieve a Post object based on its UUID.
    Args:
        post_id (str): The UUID of the post.
    Returns:
        Post: The retrieved Post object.
    Raises:
        ObjectDoesNotExist: If the post with the specified UUID does not exist.
    """
    try:
        with transaction.atomic():
            post = Post.objects.create(**post_data)
            return post

    except IntegrityError:
        raise ServiceException(status.HTTP_409_CONFLICT, ErrorCodes.RESOURCE_DUPLICATION_ATTEMPTED, f'Attempting Duplicate Post ID{post_data}')

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unable to query DB')


@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def update_post_sync(post_id, analyzed_data):
    try:
        update_dict = dict(is_analysed=True, analysed_at=datetime.datetime.now())
        update_dict.update(analyzed_data)
        updated = Post.objects.filter(uuid=post_id).update(**update_dict)
        return updated

    except (OperationalError, DatabaseError, InternalError) as e:
        raise e

    except (ValidationError, FieldError, DataError):
        raise ServiceException(status.HTTP_400_BAD_REQUEST, ErrorCodes.POST_UPDATION_ERROR, 'Unexpected analysis data')


async def retry_update_post(post_id, analyzed_data,
                            max_retries=3, base_retry_interval=1):
    for attempt in range(max_retries + 1):  # Include the initial attempt
        try:
            await update_post_sync(post_id, analyzed_data)
            break
        except (OperationalError, DatabaseError, InternalError) as e:
            logging.error(f'{post_id} update failed: {str(e)} because of database issue')
            retry_interval = base_retry_interval * (2 ** attempt)
            await asyncio.sleep(retry_interval)

        except (ValidationError, FieldError, DataError) as e:
            logging.error(f'{post_id} update failed: {str(e)} because of data issue')
            raise ServiceException(status.HTTP_400_BAD_REQUEST, ErrorCodes.POST_UPDATION_ERROR, 'Unexpected analysis data')

        except Exception as e:
            raise ServiceException(e.status_code, ErrorCodes.POST_UPDATION_ERROR, f'{e.message}')
