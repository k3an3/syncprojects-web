from django.urls import include, path
from rest_framework import routers

from sync.api import views

router = routers.DefaultRouter()
router.register(r'syncs', views.SyncViewSet, 'sync')
router.register(r'updates', views.ClientUpdateViewSet, 'update')
router.register(r'logs', views.ClientLogViewSet, 'log')

urlpatterns = [
    path('', include(router.urls)),
]
