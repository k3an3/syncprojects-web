from django.urls import include, path
from rest_framework import routers

from users.api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'user')

urlpatterns = [
    path('', include(router.urls))
]
