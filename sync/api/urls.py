from django.urls import include, path
from rest_framework import routers

from sync.api import views

router = routers.DefaultRouter()
router.register(r'syncs', views.SyncViewSet, 'sync')
router.register(r'updates', views.ClientUpdateViewSet, 'update')
router.register(r'logs', views.ClientLogViewSet, 'log')

urlpatterns = [
    path('', include(router.urls)),
    path('backend_creds/', views.get_backend_creds, name='backend_creds'),
    path('sync/audio_sync/', views.audio_sync, name='audio_sync'),
]
