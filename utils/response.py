import time
from datetime import date, datetime
from decimal import Decimal
from django.http import JsonResponse


class ResponseSerializer:

    """
    A utility class for serializing data into JSON-compatible format.

    This class provides methods for serializing various data types into JSON format
    with custom handling for datetime, date, decimal, time, and set data types.

    Usage:
        Use the static methods of this class to serialize data for API responses.

    Example:
        serialized_data = ResponseSerializer.serialize(data)
    """

    @staticmethod
    def serialize(data):
        """
        Serialize data into JSON-compatible format.

        Args:
            data (Any): The data to be serialized.

        Returns:
            Any: The serialized data.

        Note:
            This method handles serialization of datetime, date, decimal, time, and set data types.

        """
        if data is None:
            return None
        if isinstance(data, dict):
            return {key: ResponseSerializer.serialize(value) for key, value in data.items()}
        if isinstance(data, property):
            return ResponseSerializer.serialize(data.fget())
        return ResponseSerializer.json_serial(data)

    @staticmethod
    def json_serial(obj):
        """
        Serialize specific data types into JSON-compatible format.

        Args:
            obj (Any): The object to be serialized.

        Returns:
            Any: The serialized object.

        Note:
            This method handles serialization of datetime, date, decimal, time, and set data types.

        """
        if isinstance(obj, (date, datetime)):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, time.struct_time):
            return time.strftime("%Y-%m-%dT%H:%M:%S", obj)
        if isinstance(obj, set):
            return list(obj)
        return obj


class SendAsyncResponse(JsonResponse):
    """
    Custom JSON response class with serialized data.

    This class extends Django's JsonResponse and provides a way to create JSON responses
    with serialized data using the ResponseSerializer.

    Args:
        status (int): The HTTP status code for the response.
        data (Any, optional): The data to be included in the response. Defaults to None.
        message (str, optional): A message to include in the response. Defaults to an empty string.
        error_code (int, optional): An error code to include in the response. Defaults to None.
        content_type (str, optional): The content type of the response. Defaults to "application/json".

    Usage:
        Use this class to create JSON responses with serialized data and optional details.

    Example:
        response = SendAsyncResponse(status=200, data=my_data, message="Success")

    """
    def __init__(self, status, data=None, message="", error_code=None, content_type="application/json"):
        response_data = {
            "status": status,
            "data": ResponseSerializer.serialize(data),
            "message": message,
            "error_code": error_code
        }
        super().__init__(data=response_data, status=status, content_type=content_type)
