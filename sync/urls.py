from django.urls import path

from . import views

app_name = 'sync'
urlpatterns = [
    path('client_login/', views.send_sync_token, name='client-login'),
    path('client_login/success/', views.authorization_success, name='client-login-success'),
]
