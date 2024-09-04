from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import CustomUser, Project, Contributor, Issue
from .exceptions import CustomNotFound, CustomBadRequest


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

    def validate_refresh_token(self, refresh_token):
        try:
            RefreshToken(refresh_token)
        except (TokenError, InvalidToken) as e:
            raise CustomBadRequest(f"{str(e)}")
        except Exception as e:
            raise CustomBadRequest(f"Erreur de refresh token. {str(e)}")


class ContributorMixin:
    """
    Mixins related to contributors
    """
    def get_contributor(self, project_id, user_id):
        try:
            return Contributor.objects.get(user_id=user_id, project_id=project_id)
        except Contributor.DoesNotExist:
            raise CustomNotFound("Contributeur non trouvé")
