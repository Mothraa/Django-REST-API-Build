from rest_framework.exceptions import APIException
from rest_framework import status


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

