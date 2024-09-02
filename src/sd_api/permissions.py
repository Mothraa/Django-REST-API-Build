from rest_framework.permissions import BasePermission

from .models import Contributor


class IsProjectOwner(BasePermission):
    """
    Permission to check if the user is the owner of the project.
    "obj" must be a project
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(BasePermission):
    """
    Check if the user is a contributor to the project
    """
    def has_object_permission(self, request, view, obj):
        # On verifie si l'objet est une instance du projet
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj

        return Contributor.objects.filter(user=request.user, project=project).exists()
