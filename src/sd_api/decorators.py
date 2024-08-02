from functools import wraps

from rest_framework.response import Response
from rest_framework import status

from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest


def handle_exceptions(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except CustomPermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except CustomNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except CustomBadRequest as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Erreur : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper
