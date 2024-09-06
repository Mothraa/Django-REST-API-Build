from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken  # pour gérer la blacklist
from django_filters.rest_framework import DjangoFilterBackend

from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import (CustomUserSerializer,
                          CustomUserDetailSerializer,
                          CustomUserUpdateSerializer,
                          ProjectSerializer,
                          ContributorSerializer,
                          IssueSerializer,
                          CommentSerializer,
                          TokenBlacklistSerializer,
                          )
from .filters import IssueFilter, CommentFilter
from .throttles import CustomThrottle
from .mixins import ValidationMixin, ContributorMixin
from .permissions import IsMeOrAdmin, IsContributor, IsProjectOwner


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    detail_serializer_class = CustomUserDetailSerializer
    update_serializer_class = CustomUserUpdateSerializer
    throttle_classes = [CustomThrottle]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsMeOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return CustomUser.objects.all()
        # pour les utilisateurs affiche leurs infos uniquement
        return CustomUser.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return self.detail_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        return self.serializer_class

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TokenBlacklistViewSet(viewsets.ModelViewSet, ValidationMixin):
    serializer_class = TokenBlacklistSerializer
    throttle_classes = [CustomThrottle]
    http_method_names = ['post']

    def token_blacklist(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"erreur": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        serializer.save()

    def perform_destroy(self, instance):
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

        contributor = Contributor.objects.create(user=user, project=project)
        serializer = self.serializer_class(contributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, project_id=None, user_id=None):
        self.validate_project_id(project_id)
        self.validate_user_id(user_id)

        contributor = self.get_contributor(project_id, user_id)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_contributors(self, request, project_id=None):
        self.validate_project_id(project_id)
        project = Project.objects.get(pk=project_id)

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
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH
    filterset_class = IssueFilter
    filterset_fields = ['project']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsMeOrAdmin]
        else:
            permission_classes = [IsAuthenticated, IsContributor | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        # si admin retourne tout
        if user.is_superuser or user.is_staff:
            return Issue.objects.all()
        # sinon retourne que ses Issues
        return Issue.objects.filter(project__contributors__user=user)

    def perform_create(self, serializer):
        print("Requête de données : ", self.request.data)
        user = self.request.user
        project = serializer.validated_data.get('project')
        # si pas d'assignation de l'issue, met par défaut le créateur
        assignee = serializer.validated_data.get('assignee', user)

        self.validate_project_id(project.id)
        self.validate_user_id(assignee.id)

        serializer.save(project=project, author=user, assignee=assignee)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet, ValidationMixin):
    serializer_class = CommentSerializer
    throttle_classes = [CustomThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
    http_method_names = ['get', 'post', 'put', 'delete']  # on n'authorise pas le PATCH

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsMeOrAdmin]
        else:
            permission_classes = [IsAuthenticated, IsContributor | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        # si admin retourne tout
        if user.is_superuser or user.is_staff:
            return Comment.objects.all()
        # sinon retourne que ses les comments auquel l'user a accès
        return Comment.objects.filter(issue__project__contributors__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        issue_id = self.request.data.get('issue')
        issue = self.validate_issue_id(issue_id)
        serializer.save(author=user, issue=issue)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
