from rest_framework import status
from django.http import JsonResponse


def error_404(request, exception):
    """
    Custom handler for 404 request.
    """
    response = JsonResponse(data={'message': 'Route not found', 'status': status.HTTP_404_NOT_FOUND})
    response.status_code = 404
    return response


def error_500(request):
    """
    Custom handler for 500 request.
    """
    response = JsonResponse(data={'message': 'Internal server error', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
    response.status_code = 500
    return response
