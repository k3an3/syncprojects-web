from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import ProjectViewSet, update_webhook, peaks, \
    sign_data, SongViewSet, fetch_user_tokens
from comments.api.urls import router as comments_router
from player.api.urls import router as player_router
from snippets.api.urls import router as snippets_router
from sync.api.urls import router as sync_router
from sync.api.views import get_backend_creds
from users.api.urls import router as users_router

router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet, 'project')
router.register(r'songs', SongViewSet, 'song')

# Submodule APIs
router.registry.extend(player_router.registry)
router.registry.extend(users_router.registry)
router.registry.extend(comments_router.registry)
router.registry.extend(sync_router.registry)
router.registry.extend(snippets_router.registry)

urlpatterns = [
    path('', include(router.urls)),
    path('player/', include(player_router.urls)),
    path('sync/', include('sync.api.urls')),
    path('todo/', include('todo.api.urls')),
    path('sign/', sign_data, name='sign_data'),
    path('peaks/', peaks, name='peaks'),
    path('token/fetch/', fetch_user_tokens),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('webauth/', include('rest_framework.urls', namespace='rest_framework')),
    path('webhook/update/', update_webhook, name='update_webhook'),
    path('backend_creds/', get_backend_creds, name='backend_creds'),
]
