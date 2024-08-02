from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, ProjectViewSet, ContributorViewSet, IssueViewSet, CommentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('projects', ProjectViewSet, basename='projects')
router.register('contributors', ContributorViewSet, basename='contributors')
router.register('issues', IssueViewSet, basename='issue')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
     path('api-auth/', include('rest_framework.urls')),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('api/', include(router.urls)),
     # spécifique contributors
     path('api/projects/<int:project_id>/contributors/',
          ContributorViewSet.as_view({'post': 'create', 'get': 'list_contributors'}),
          name='project-contributors-list'),
     path('api/projects/<int:project_id>/contributors/<int:user_id>/',
          ContributorViewSet.as_view({'delete': 'destroy'}),
          name='project-contributor-manage'),
     path('api/users/<int:user_id>/projects/',
          ContributorViewSet.as_view({'get': 'user_projects'}),
          name='user-projects'),
]
