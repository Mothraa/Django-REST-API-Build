from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, ProjectViewSet, ContributorViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('projects', ProjectViewSet, basename='projects')
router.register('contributors', ContributorViewSet, basename='contributor')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/projects/<int:project_id>/contributors/',
         ContributorViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='project-contributor-add'),
    path('api/projects/<int:project_id>/contributors/<int:user_id>/',
         ContributorViewSet.as_view({'delete': 'destroy'}),
         name='project-contributor-remove'),
]
