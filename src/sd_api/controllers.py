# from rest_framework.response import Response
# from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from .models import CustomUser, Project, Contributor, Issue
from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest


# class BaseValidator
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
        return Project.objects.get(pk=project_id)

    @staticmethod
    def validate_user_id(user_id):
        """
        Validate the user ID
        """
        if user_id is None:
            raise CustomBadRequest("L'ID de l'utilisateur est requis")
        if not CustomUser.objects.filter(pk=user_id).exists():
            raise CustomNotFound("Utilisateur non trouvé")
        return CustomUser.objects.get(pk=user_id)

    @staticmethod
    def validate_issue_id(issue_id):
        """
        Validate the issue ID
        """

        if issue_id is None:
            raise CustomBadRequest("L'ID de l'issue est requis")
        if not Issue.objects.filter(pk=issue_id).exists():
            raise CustomNotFound("Issue non trouvée")
        return Issue.objects.get(pk=issue_id)

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
        Check if the user can access the project.
        """
        print(f'Checking permissions for user: {user}')
        print(f'Project ID: {project.id}')

        all_contributors = project.contributors.all()

        is_contributor = all_contributors.filter(user=user).exists()
        print(f'Is contributor: {is_contributor}')

        is_superuser = user.is_superuser

        if not is_contributor and not is_superuser:
            raise CustomPermissionDenied(f"L'utilisateur {user} n'a pas la permission d'accéder à ce projet")

        # if not project.contributors.filter(user=user).exists() and not user.is_superuser:
        #     print("exception !")
        #     # print(type(PermissionDenied(f"L'utilisateur {user} n'a pas la permission d'accéder à ce projet")))
        #     raise CustomPermissionDenied()
        #     # raise PermissionDenied(f"L'utilisateur {user} n'a pas la permission d'accéder à ce projet")
        #     # raise CustomPermissionDenied(f"L'utilisateur {user} n'a pas la permission d'accéder à ce projet")

    @staticmethod
    def check_contributor_permission(user, contributor):
        """
        Check if the user is authorized to remove the contributor
        """
        if contributor.project.author != user:
            raise CustomPermissionDenied("Vous n'avez pas la permission d'enlever ce contributeur")

    @staticmethod
    def check_user_modify_permission(user, serializer_instance):
        """
        Check if the user has the permission to modify data (superuser or their own data).
        """
        if user.is_superuser or serializer_instance.pk == user.pk:
            return True

        raise CustomPermissionDenied("Vous ne pouvez modifier que vos propres données.")

    @staticmethod
    def check_user_delete_permission(user, instance):
        """
        Check if the user has the permission to delete data (superuser or their own data).
        """

        if user.is_superuser or instance.pk == user.pk:
            return True

        # on récupère le type de l'instance (projet, issue, user, ...)
        instance_type = type(instance).__name__
        raise CustomPermissionDenied(f"Vous n'avez pas la permission de supprimer ce élément {instance_type}.")

    @staticmethod
    def get_contributor(project_id, user_id):
        """
        Retrieve the contributor
        """
        try:
            return Contributor.objects.get(user_id=user_id, project_id=project_id)
        except Contributor.DoesNotExist:
            raise CustomNotFound("Contributeur non trouvé")
