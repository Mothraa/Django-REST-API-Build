from rest_framework.response import Response
from rest_framework import viewsets, status, filters
# from rest_framework.exceptions import PermissionDenied, NotFound
# from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import (CustomUserSerializer,
                          CustomUserDetailSerializer,
                          CustomUserUpdateSerializer,
                          ProjectSerializer,
                          ContributorSerializer,
                          # ProjectUpdateSerializer,
                          IssueSerializer,
                          CommentSerializer,
                          )
from .filters import IssueFilter, CommentFilter
from .controllers import ValidationController
from .throttles import CustomThrottle
from .decorators import handle_exceptions


# import logging
# logger = logging.getLogger(__name__)


# LoginRequiredMixin et PermissionRequiredMixin et UserPassesTestMixin

# Un ModelViewset  est comparable à une super vue Django qui regroupe à la fois CreateView, UpdateView, DeleteView, ListView et DetailView.
# class CategoryViewset(ReadOnlyModelViewSet):


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    detail_serializer_class = CustomUserDetailSerializer
    update_serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    @handle_exceptions
    def get_queryset(self):
        user = self.request.user
        # logger.debug(f"User: {user}")
        if user.is_superuser or user.is_staff:
            # print("is superuser")
            return CustomUser.objects.all()
        # pour que les utilisateurs puissent voir leurs propres infos
        return CustomUser.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        # TODO ajouter des exceptions
        if self.action in ['retrieve']:
            return self.detail_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        return self.serializer_class

    @handle_exceptions
    def perform_update(self, serializer):
        user = self.request.user
        ValidationController.check_user_modify_permission(user, serializer.instance)
        serializer.save()

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        ValidationController.check_user_delete_permission(user, instance)
        return super().destroy(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(contributors__user=user)

    @handle_exceptions
    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    @handle_exceptions
    def perform_update(self, serializer):
        user = self.request.user
        project = self.get_object()
        ValidationController.check_project_permission(self.request.user, project)
        ValidationController.check_user_modify_permission(user, project)
        serializer.save()

    @handle_exceptions
    def perform_destroy(self, instance):
        user = self.request.user
        project = instance
        ValidationController.check_project_permission(user, instance)
        ValidationController.check_user_delete_permission(user, project)
        instance.delete()

    # @action(detail=True, methods=['post'])
    # def action_perso(self):
    #     pass


class ContributorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer
    project_serializer_class = ProjectSerializer
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    @handle_exceptions
    def create(self, request, project_id=None):
        # récupération de l'user_id via le body
        user_id = request.data.get('user_id')

        ValidationController.validate_project_id(project_id)
        ValidationController.validate_user_id(user_id)

        project = Project.objects.get(pk=project_id)
        user = CustomUser.objects.get(pk=user_id)

        ValidationController.check_contributor_exist(user, project)
        ValidationController.check_project_permission(request.user, project)

        contributor = Contributor.objects.create(user=user, project=project)
        serializer = self.serializer_class(contributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @handle_exceptions
    def destroy(self, request, project_id=None, user_id=None):
        ValidationController.validate_project_id(project_id)
        ValidationController.validate_user_id(user_id)

        contributor = ValidationController.get_contributor(project_id, user_id)
        ValidationController.check_contributor_permission(request.user, contributor)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @handle_exceptions
    def list_contributors(self, request, project_id=None):
        ValidationController.validate_project_id(project_id)
        project = Project.objects.get(pk=project_id)
        ValidationController.check_project_permission(request.user, project)

        contributors = Contributor.objects.filter(project=project)
        serializer = self.serializer_class(contributors, many=True)
        return Response(serializer.data)

    @handle_exceptions
    def user_projects(self, request, user_id=None):
        ValidationController.validate_user_id(user_id)
        user = CustomUser.objects.get(pk=user_id)
        projects = Project.objects.filter(contributors__user=user)
        serializer = self.project_serializer_class(projects, many=True)
        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH
    filterset_class = IssueFilter
    # authentication_classes = [] # You still need to declare it even it is empty
    
    # filterset_fields = ['project']

    def get_queryset(self):
        user = self.request.user
        # retourne que les issues pour lesquels le user est concerné (contributor)
        return Issue.objects.filter(project__contributors__user=user)

    @handle_exceptions
    def perform_create(self, serializer):
        # si pas d'assignation de l'issue, mettre par défaut le créateur
        # if 'assignee' not in serializer.validated_data:
        #     serializer.save(assignee=self.request.user)
        # else:
        #     serializer.save()
        user = self.request.user
        # project_id = self.request.data.get('project')
        project_id = serializer.validated_data.get('project')
        # assignee_id = self.request.data.get('assignee')
        assignee_id = serializer.validated_data.get('assignee')

        project = ValidationController.validate_project_id(project_id)
        ValidationController.check_project_permission(user, project)

        # TODO BUG : erreur, possible d'assigner un user qui n'est pas dans le projet
        if assignee_id:
            # ValidationController.validate_user_id(assignee_id)
            # assignee = CustomUser.objects.get(pk=assignee_id)

            assignee = ValidationController.validate_user_id(assignee_id)
            ValidationController.check_project_permission(assignee, project)
        else:
            # si pas d'assignation de l'issue, met par défaut le créateur
            assignee = user

        serializer.save(project=project, author=user, assignee=assignee)

    @handle_exceptions
    def perform_update(self, serializer):
        issue = self.get_object()
        user = self.request.user

        ValidationController.check_project_permission(user, issue.project)
        ValidationController.check_user_modify_permission(user, issue)

        assignee = serializer.validated_data.get('assignee')
        if assignee:
            #     assignee = ValidationController.validate_user_id(assignee)
            ValidationController.check_project_permission(assignee, issue.project)

        # data = serializer.validated_data
        # data.pop('project', None)
        # data.pop('author', None)
        # data.pop('created_time', None)

        # serializer.save(**data)
        serializer.save()

    @handle_exceptions
    def perform_destroy(self, instance):
        user = self.request.user

        ValidationController.check_project_permission(user, instance.project)
        ValidationController.check_user_delete_permission(user, instance)
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH
    filterset_class = CommentFilter

    def get_queryset(self):
        user = self.request.user
        # Filtrage des comments pour les issues auquel l'user à accès
        return Comment.objects.filter(issue__project__contributors__user=user)

    @handle_exceptions
    def perform_create(self, serializer):
        user = self.request.user
        issue_id = self.request.data.get('issue')

        issue = ValidationController.validate_issue_id(issue_id)
        ValidationController.check_project_permission(user, issue.project)
        serializer.save(author=user, issue=issue)

    @handle_exceptions
    def perform_update(self, serializer):
        comment = self.get_object()
        user = self.request.user

        ValidationController.check_project_permission(user, comment.issue.project)
        ValidationController.check_user_modify_permission(user, comment)

        serializer.save()

    @handle_exceptions
    def perform_destroy(self, instance):
        user = self.request.user

        ValidationController.check_project_permission(user, instance.issue.project)
        ValidationController.check_user_delete_permission(user, instance)
        instance.delete()
