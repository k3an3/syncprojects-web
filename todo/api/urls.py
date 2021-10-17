from django.urls import path
from rest_framework import routers

from todo.api import views

router = routers.DefaultRouter()

urlpatterns = [
    path('check/', views.handle_check, name='todo_check'),
]
