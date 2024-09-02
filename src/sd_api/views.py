from rest_framework.response import Response
from rest_framework import viewsets, status, filters
# from rest_framework.exceptions import PermissionDenied, NotFound
# from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

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
from .throttles import CustomThrottle
from .mixins import ValidationMixin, ContributorMixin
from .permissions import IsContributor, IsProjectOwner

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

    # TODO gestion des permissions
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
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

    def perform_update(self, serializer):
        self.check_user_modify_permission(self.request.user, serializer.instance)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        self.check_user_delete_permission(user, instance)
        return super().destroy(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet, ValidationMixin):
    serializer_class = ProjectSerializer
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsProjectOwner | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsContributor | IsAdminUser | IsProjectOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(contributors__user=user)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    def perform_update(self, serializer):
        user = self.request.user
        project = self.get_object()
        self.check_project_permission(self.request.user, project)
        self.check_user_modify_permission(user, project)
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        project = instance
        # self.check_project_permission(user, instance)
        # self.check_user_delete_permission(user, project)
        instance.delete()


class ContributorViewSet(viewsets.ViewSet, ValidationMixin, ContributorMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer
    project_serializer_class = ProjectSerializer
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    def create(self, request, project_id=None):
        # récupération de l'user_id via le body
        user_id = request.data.get('user_id')

        self.validate_project_id(project_id)
        self.validate_user_id(user_id)

        project = Project.objects.get(pk=project_id)
        user = CustomUser.objects.get(pk=user_id)

        # self.check_contributor_exist(user, project)
        self.check_project_permission(request.user, project)

        contributor = Contributor.objects.create(user=user, project=project)
        serializer = self.serializer_class(contributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, project_id=None, user_id=None):
        self.validate_project_id(project_id)
        self.validate_user_id(user_id)

        contributor = self.get_contributor(project_id, user_id)
        self.check_contributor_permission(request.user, contributor)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_contributors(self, request, project_id=None):
        self.validate_project_id(project_id)
        project = Project.objects.get(pk=project_id)
        self.check_project_permission(request.user, project)

        contributors = Contributor.objects.filter(project=project)
        serializer = self.serializer_class(contributors, many=True)
        return Response(serializer.data)

    def user_projects(self, request, user_id=None):
        self.validate_user_id(user_id)
        user = CustomUser.objects.get(pk=user_id)
        projects = Project.objects.filter(contributors__user=user)
        serializer = self.project_serializer_class(projects, many=True)
        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet, ValidationMixin):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributor | IsAdminUser]
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH
    filterset_class = IssueFilter
    # filterset_fields = ['project']

    def get_queryset(self):
        user = self.request.user
        # retourne que les issues pour lesquels le user est concerné (contributor)
        return Issue.objects.filter(project__contributors__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        project_id = serializer.validated_data.get('project')
        assignee_id = serializer.validated_data.get('assignee')

        project = self.validate_project_id(project_id)
        self.check_project_permission(user, project)

        if assignee_id:
            assignee = self.validate_user_id(assignee_id)
            self.check_project_permission(assignee, project)
        else:
            # si pas d'assignation de l'issue, met par défaut le créateur
            assignee = user

        serializer.save(project=project, author=user, assignee=assignee)

    def perform_update(self, serializer):
        issue = self.get_object()
        user = self.request.user

        self.check_project_permission(user, issue.project)
        self.check_user_modify_permission(user, issue)

        assignee = serializer.validated_data.get('assignee')
        if assignee:
            self.check_project_permission(assignee, issue.project)

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        self.check_project_permission(user, instance.project)
        self.check_user_delete_permission(user, instance)
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet, ValidationMixin):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributor | IsAdminUser]
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH
    filterset_class = CommentFilter

    def get_queryset(self):
        user = self.request.user
        # Filtrage des comments pour les issues auquel l'user à accès
        return Comment.objects.filter(issue__project__contributors__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        issue_id = self.request.data.get('issue')

        issue = self.validate_issue_id(issue_id)
        self.check_project_permission(user, issue.project)
        serializer.save(author=user, issue=issue)

    def perform_update(self, serializer):
        comment = self.get_object()
        user = self.request.user
        self.check_project_permission(user, comment.issue.project)
        self.check_user_modify_permission(user, comment)
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        self.check_project_permission(user, instance.issue.project)
        self.check_user_delete_permission(user, instance)
        instance.delete()
