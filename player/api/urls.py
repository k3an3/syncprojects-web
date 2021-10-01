from rest_framework import routers

from player.api import views

router = routers.DefaultRouter()
router.register(r'regions', views.SongRegionViewSet, 'regions')

urlpatterns = [
]
