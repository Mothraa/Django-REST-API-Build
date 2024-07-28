# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, Project, Contributor
from .serializers import (CustomUserSerializer,
                          CustomUserDetailSerializer,
                          CustomUserUpdateSerializer,
                          ProjectSerializer,
                          ContributorSerializer,
                        #   ProjectUpdateSerializer,
                          )
# from .permissions import IsAdminAuthenticated


#LoginRequiredMixin et PermissionRequiredMixin et UserPassesTestMixin

# Un ModelViewset  est comparable à une super vue Django qui regroupe à la fois CreateView, UpdateView, DeleteView, ListView  et DetailView.
# class CategoryViewset(ReadOnlyModelViewSet):


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    detail_serializer_class = CustomUserDetailSerializer
    update_serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]  # Changer pour IsAuthenticated pour permettre aux utilisateurs de mettre à jour leurs propres données

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            # Les superadmin et le staff peuvent voir la liste de tous les utilisateurs
            return CustomUser.objects.all()
        # Les utilisateurs réguliers ne peuvent pas voir la liste des utilisateurs
        return CustomUser.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return self.detail_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        return self.serializer_class

    def perform_update(self, serializer):
        # S'assurer que l'utilisateur ne peut mettre à jour que ses propres données, sauf s'il est administrateur
        user = self.request.user
        if user.is_superuser:
            # Seul le superuser peut modifier n'importe quel utilisateur
            serializer.save()
        else:
            # Les utilisateurs réguliers ne peuvent mettre à jour que leurs propres données
            if serializer.instance.pk == user.pk:
                serializer.save()
            else:
                raise PermissionDenied("Vous n'avez pas la permission de modifier cet utilisateur.")

    def destroy(self, request, *args, **kwargs):
        # Seul le superadmin peut supprimer un compte. Un compte doit pouvoir s'autodétruire
        user = self.request.user
        instance = self.get_object()

        if user.is_superuser or instance.pk == user.pk:
            # Les superadmin peuvent supprimer n'importe quel compte
            # Les utilisateurs réguliers peuvent supprimer leur propre compte
            return super().destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer cet utilisateur.")


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
        # ajoute l'utilisateur comme contributeur
        Contributor.objects.create(user=self.request.user, project=project)

    def perform_update(self, serializer):
        # seul l'auteur du projet peut le modifier
        project = self.get_object()
        if project.author == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied("Vous n'avez pas la permission de modifier ce projet.")

    def perform_destroy(self, instance):
        # Seul l'auteur du projet peut supprimer le projet
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce projet.")

    # @action(detail=True, methods=['post'])
    # def action_perso(self):
    #     pass


class ContributorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer
    project_serializer_class = ProjectSerializer

    def create(self, request, project_id=None):
        user_id = request.data.get('user')
        if user_id is None:
            return Response({"detail": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise NotFound("Aucun projet trouvé")

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound("Aucun utilisateur trouvé")

        if Contributor.objects.filter(user=user, project=project).exists():
            raise PermissionDenied("Ce contributeur est déjà ajouté au projet")

        if project.author != request.user:
            raise PermissionDenied("Vous ne pouvez pas ajouter de contributeurs")

        contributor = Contributor.objects.create(user=user, project=project)
        serializer = self.serializer_class(contributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, project_id=None, user_id=None):
        if user_id is None:
            return Response({"detail": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            contributor = Contributor.objects.get(user_id=user_id, project_id=project_id)
        except Contributor.DoesNotExist:
            raise NotFound("Aucun contributeur trouvé")

        if contributor.project.author != request.user:
            raise PermissionDenied("Vous ne pouvez pas supprimer de contributeurs")

        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_contributors(self, request, project_id=None):
        if project_id is None:
            return Response({"detail": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise NotFound("Aucun projet trouvé")

        if project.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("Vous n'avez pas la permission de voir les contributeurs de ce projet")

        contributors = Contributor.objects.filter(project=project)
        serializer = self.serializer_class(contributors, many=True)
        return Response(serializer.data)

    def list_projects(self, request, user_id=None):
        if user_id is None:
            return Response({"Un ID utilisateur est requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound("Aucun utilisateur trouvé")

        projects = Project.objects.filter(contributors__user=user)
        serializer = self.project_serializer_class(projects, many=True)
        return Response(serializer.data)
