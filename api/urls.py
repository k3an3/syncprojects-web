from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import UserViewSet, ProjectViewSet, fetch_user_tokens, update_webhook, peaks, \
    ClientUpdateViewSet, sign_data, SyncViewSet, get_backend_creds, SongViewSet, ClientLogViewSet, CommentViewSet, \
    audio_sync
from player.api.urls import router as player_router

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, 'user')
router.register(r'updates', ClientUpdateViewSet, 'update')
router.register(r'projects', ProjectViewSet, 'project')
router.register(r'syncs', SyncViewSet, 'sync')
router.register(r'songs', SongViewSet, 'song')
router.register(r'logs', ClientLogViewSet, 'log')
router.register(r'comments', CommentViewSet, 'comment')

# Submodule APIs
router.registry.extend(player_router.registry)

urlpatterns = [
    path('', include(router.urls)),
    path('player/', include(player_router.urls)),
    path('sign/', sign_data, name='sign_data'),
    path('peaks/', peaks, name='peaks'),
    path('token/fetch/', fetch_user_tokens),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('webauth/', include('rest_framework.urls', namespace='rest_framework')),
    path('webhook/update/', update_webhook, name='update_webhook'),
    path('backend_creds/', get_backend_creds, name='backend_creds'),
    path('sync/audio_sync/', audio_sync, name='audio_sync'),
]
