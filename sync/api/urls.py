from django.urls import path
from rest_framework import routers

from sync.api import views

router = routers.DefaultRouter()
router.register(r'syncs', views.SyncViewSet, 'sync')
router.register(r'updates', views.ClientUpdateViewSet, 'update')
router.register(r'logs', views.ClientLogViewSet, 'log')

urlpatterns = [
    path('audio_sync/', views.audio_sync, name='audio_sync'),
    path('checkouts/', views.get_checkouts, name='get_checkouts'),
]
