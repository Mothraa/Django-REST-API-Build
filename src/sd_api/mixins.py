from .models import CustomUser, Project, Contributor, Issue
from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest


class ValidationMixin:
    """
    Mixins for validate IDs
    """
    def validate_project_id(self, project_id):
        if project_id is None:
            raise CustomBadRequest("L'ID du projet est requis")
        if not Project.objects.filter(pk=project_id).exists():
            raise CustomNotFound("Projet non trouvé")
        return Project.objects.get(pk=project_id)

    def validate_user_id(self, user_id):
        if user_id is None:
            raise CustomBadRequest("L'ID de l'utilisateur est requis")
        if not CustomUser.objects.filter(pk=user_id).exists():
            raise CustomNotFound("Utilisateur non trouvé")
        return CustomUser.objects.get(pk=user_id)

    def validate_issue_id(self, issue_id):
        if issue_id is None:
            raise CustomBadRequest("L'ID de l'issue est requis")
        if not Issue.objects.filter(pk=issue_id).exists():
            raise CustomNotFound("Issue non trouvée")
        return Issue.objects.get(pk=issue_id)


# class PermissionMixin:
#     """
#     Mixins for checking permissions
#     """
#     def check_project_permission(self, user, project):
#         all_contributors = project.contributors.all()
#         is_contributor = all_contributors.filter(user=user).exists()
#         is_superuser = user.is_superuser

#         if not is_contributor and not is_superuser:
#             raise CustomPermissionDenied(f"L'utilisateur {user} n'a pas la permission d'accéder à ce projet")

#     def check_contributor_permission(self, user, contributor):
#         if contributor.project.author != user:
#             raise CustomPermissionDenied("Vous n'avez pas la permission d'enlever ce contributeur")

#     def check_user_modify_permission(self, user, serializer_instance):
#         if user.is_superuser or serializer_instance.pk == user.pk:
#             return True
#         raise CustomPermissionDenied("Vous ne pouvez modifier que vos propres données")

#     def check_user_delete_permission(self, user, instance):
#         if user.is_superuser or instance.pk == user.pk:
#             return True
#         instance_type = type(instance).__name__
#         raise CustomPermissionDenied(f"Vous n'avez pas la permission de supprimer cet élément {instance_type}.")


class ContributorMixin:
    """
    Mixins related to contributors
    """
    def get_contributor(self, project_id, user_id):
        try:
            return Contributor.objects.get(user_id=user_id, project_id=project_id)
        except Contributor.DoesNotExist:
            raise CustomNotFound("Contributeur non trouvé")
