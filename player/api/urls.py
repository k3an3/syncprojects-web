from django.urls import include, path
from rest_framework import routers

from player.api import views

router = routers.DefaultRouter()
router.register(r'regions', views.SongRegionViewSet, 'regions')

urlpatterns = [
    path('', include(router.urls))
]
