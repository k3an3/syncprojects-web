from django.urls import path

from . import views

app_name = 'sync'
urlpatterns = [
    path('client_login/', views.send_sync_token, name='client_login'),
]
