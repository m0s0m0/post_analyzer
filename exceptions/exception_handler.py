import traceback
from rest_framework.views import exception_handler
from rest_framework import status
from exceptions.service_error import ServiceException


from django.http import JsonResponse



def error_404(request, exception):
    """
    custom handler for 404 request

    """
    response =  JsonResponse(data={'message': 'Route not found', 'status':status.HTTP_404_NOT_FOUND})
    response.status_code = 404
    return response

def error_500(request):
    """
    custom handler for 500 request

    """
    response =  JsonResponse(data={'message': 'Route not found', 'status':status.HTTP_500_INTERNAL_SERVER_ERROR})
    response.status_code=500
    return response