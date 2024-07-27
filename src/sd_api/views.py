# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
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


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Contributor.objects.filter(user=user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if project.author != self.request.user:
            raise PermissionDenied("Vous ne pouvez pas ajouter de contributeurs")
        serializer.save()

    def perform_destroy(self, instance):
        project = instance.project
        if project.author != self.request.user:
            raise PermissionDenied("Vous ne pouvez pas supprimer de contributeurs")
        instance.delete()