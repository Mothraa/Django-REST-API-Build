# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserDetailSerializer, CustomUserUpdateSerializer
from .permissions import IsAdminAuthenticated


#LoginRequiredMixin et PermissionRequiredMixin et UserPassesTestMixin

# Un ModelViewset  est comparable à une super vue Django qui regroupe à la fois CreateView, UpdateView, DeleteView, ListView  et DetailView.
# class CategoryViewset(ReadOnlyModelViewSet):

class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    detail_serializer_class = CustomUserDetailSerializer
    update_serializer_class = CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]  # Change to IsAuthenticated to allow users to update their own data

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        # Optional: Filter by category_id if provided
        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return self.detail_serializer_class
        elif self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        return self.serializer_class

    def perform_update(self, serializer):
        # Ensure that the user can only update their own data unless they are an admin
        user = self.request.user
        if user.is_superuser or user.is_staff:
            # Admin users can update any user data
            serializer.save()
        else:
            # Regular users can only update their own data
            if serializer.instance.pk == user.pk:
                serializer.save()
            else:
                raise PermissionDenied("You do not have permission to edit this user.")