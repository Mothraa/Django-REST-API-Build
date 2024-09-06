from rest_framework.permissions import BasePermission

from .models import Contributor, Project, Issue, Comment


class IsMeOrAdmin(BasePermission):
    """
    Permission for the user or an admin (for ex : delete his own account)
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.author == request.user


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
        # On recupère l'instance du projet en fonction du type d'objet source
        if isinstance(obj, Comment):
            project = obj.issue.project
        elif isinstance(obj, Issue):
            project = obj.project
        elif isinstance(obj, Project):
            project = obj
        else:
            return False

        # On regarde si l'utilisateur est contributeur du projet
        return Contributor.objects.filter(user=request.user, project=project).exists()
