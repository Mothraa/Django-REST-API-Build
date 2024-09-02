from rest_framework.exceptions import APIException
from rest_framework import status

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        # response.data['status_code'] = 666
        response.data['detail'] = str(exc)
    # Vérifier si la réponse est une liste ou un dictionnaire
    # print(type(response.data))
    # if response is not None:
    #     if isinstance(response.data, dict):  # Assurez-vous que response.data est un dict
    #         # response.data['status_code'] = '666'
    #         response.data['detail'] = str(exc)
    #     else:
    #         # Si response.data est une liste, gérer ce cas spécifique ici
    #         response.data = {
    #             'status_code': '666',
    #             'detail': str(exc),
    #             'errors': response.data
    #         }

    return response


class CustomPermissionDenied(APIException):
    """
    Exception for errors of permissions
    """
    # print("inside exception !")
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Action interdite'
    default_code = 'permission_denied'
    message = "T'as pas le droit !"


class CustomNotFound(APIException):
    """
    Exception when something is not found
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Non trouvé'
    default_code = 'not_found'


class CustomBadRequest(APIException):
    """
    Exception when bad request.
    """
    status_code = status.HTTP_400_BAD_REQUEST

