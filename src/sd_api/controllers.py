# from rest_framework.response import Response
# from rest_framework import status
from .models import CustomUser, Project, Contributor
from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest


class ValidationController:
    @staticmethod
    def validate_project_id(project_id):
        """
        Validate the project ID
        """
        if project_id is None:
            raise CustomBadRequest("L'ID du projet est requis")
        if not Project.objects.filter(pk=project_id).exists():
            raise CustomNotFound("Projet non trouvé")
        return None

    @staticmethod
    def validate_user_id(user_id):
        """
        Validate the user ID
        """
        if user_id is None:
            raise CustomBadRequest("L'ID de l'utilisateur est requis")
        if not CustomUser.objects.filter(pk=user_id).exists():
            raise CustomNotFound("Utilisateur non trouvé")
        return None

    @staticmethod
    def check_contributor_exist(user, project):
        """
        Check if the contributor is already associated with the project
        """
        if Contributor.objects.filter(user=user, project=project).exists():
            raise CustomPermissionDenied("Ce contributeur est déjà associé au projet")

    @staticmethod
    def check_project_permission(user, project):
        """
        Check if the user can access the project
        """
        if project.author != user:
            raise CustomPermissionDenied("Vous n'avez pas la permission d'acceder a ce projet")

    @staticmethod
    def check_contributor_permission(user, contributor):
        """
        Check if the user is authorized to remove the contributor
        """
        if contributor.project.author != user:
            raise CustomPermissionDenied("Vous n'avez pas la permission d'enlever ce contributeur")

    @staticmethod
    def check_user_permission(user, serializer_instance):
        """
        Check if the user has the permission to modify data (superuser or their own data).
        """
        if user.is_superuser:
            return
        if serializer_instance.pk != user.pk:
            raise CustomPermissionDenied("Vous ne pouvez modifier que vos propres données.")

    @staticmethod
    def check_user_delete_permission(user, instance):
        """
        Check if the user is authorized to delete the account (superuser or his own account)
        """
        if user.is_superuser or instance.pk == user.pk:
            return
        raise CustomPermissionDenied("Vous n'avez pas la permission de supprimer ce compte")

    @staticmethod
    def get_contributor(project_id, user_id):
        """
        Retrieve the contributor
        """
        try:
            return Contributor.objects.get(user_id=user_id, project_id=project_id)
        except Contributor.DoesNotExist:
            raise CustomNotFound("Contributeur non trouvé")
