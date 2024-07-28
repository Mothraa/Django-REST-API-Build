# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
# from rest_framework.exceptions import PermissionDenied, NotFound
from .exceptions import CustomPermissionDenied, CustomNotFound, CustomBadRequest
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, Project, Contributor
from .serializers import (CustomUserSerializer,
                          CustomUserDetailSerializer,
                          CustomUserUpdateSerializer,
                          ProjectSerializer,
                          ContributorSerializer,
                          # ProjectUpdateSerializer,
                          )
# from .permissions import IsAdminAuthenticated
from .controllers import ValidationController

# LoginRequiredMixin et PermissionRequiredMixin et UserPassesTestMixin

# Un ModelViewset  est comparable à une super vue Django qui regroupe à la fois CreateView, UpdateView, DeleteView, ListView  et DetailView.
# class CategoryViewset(ReadOnlyModelViewSet):


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    detail_serializer_class = CustomUserDetailSerializer
    update_serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return self.detail_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        return self.serializer_class

    def perform_update(self, serializer):
        user = self.request.user
        ValidationController.check_user_permission(user, serializer.instance)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        ValidationController.check_user_delete_permission(user, instance)
        return super().destroy(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    # detail_serializer_class = ProjectSerializerSerializer
    # update_serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(contributors__user=user)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    def perform_update(self, serializer):
        project = self.get_object()
        ValidationController.check_project_permission(self.request.user, project)
        serializer.save()

    def perform_destroy(self, instance):
        ValidationController.check_project_permission(self.request.user, instance)
        instance.delete()

    # @action(detail=True, methods=['post'])
    # def action_perso(self):
    #     pass


class ContributorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer
    project_serializer_class = ProjectSerializer

    def create(self, request, project_id=None, user_id=None):
        try:
            ValidationController.validate_project_id(project_id)
            ValidationController.validate_user_id(user_id)

            project = Project.objects.get(pk=project_id)
            user = CustomUser.objects.get(pk=user_id)

            ValidationController.check_contributor_exist(user, project)
            ValidationController.check_project_permission(request.user, project)

            contributor = Contributor.objects.create(user=user, project=project)
            serializer = self.serializer_class(contributor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except (CustomNotFound, CustomPermissionDenied, CustomBadRequest) as e:
            return Response({"detail": str(e)}, status=e.status_code)

    def destroy(self, request, project_id=None, user_id=None):
        try:
            ValidationController.validate_project_id(project_id)
            ValidationController.validate_user_id(user_id)

            contributor = ValidationController.get_contributor(project_id, user_id)
            ValidationController.check_contributor_permission(request.user, contributor)
            contributor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except (CustomNotFound, CustomPermissionDenied, CustomBadRequest) as e:
            return Response({"detail": str(e)}, status=e.status_code)

    def list_contributors(self, request, project_id=None):
        try:
            ValidationController.validate_project_id(project_id)
            project = Project.objects.get(pk=project_id)
            ValidationController.check_project_permission(request.user, project)

            contributors = Contributor.objects.filter(project=project)
            serializer = self.serializer_class(contributors, many=True)
            return Response(serializer.data)

        except (CustomNotFound, CustomPermissionDenied, CustomBadRequest) as e:
            return Response({"detail": str(e)}, status=e.status_code)

    def list_projects(self, request, user_id=None):
        try:
            ValidationController.validate_user_id(user_id)
            user = CustomUser.objects.get(pk=user_id)
            projects = Project.objects.filter(contributors__user=user)
            serializer = self.project_serializer_class(projects, many=True)
            return Response(serializer.data)

        except (CustomNotFound, CustomBadRequest) as e:
            return Response({"detail": str(e)}, status=e.status_code)
