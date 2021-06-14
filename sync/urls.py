from django.urls import path

from . import views

app_name = 'sync'
urlpatterns = [
    path('client_login/', views.send_sync_token, name='client-login'),
    path('client_login/success/', views.authorization_success, name='client-login-success'),
    path('download/', views.DownloadIndexView.as_view(), name='download-index'),
    path('logs/<int:user>/', views.UserLogIndexView.as_view(), name='log-index'),
    path('logs/<int:user>/<int:pk>', views.UserLogDetailView.as_view(), name='log-detail'),
]
