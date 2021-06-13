from django.urls import path

from users import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.UserDetailView.as_view(), name='user-profile'),
    path('profile/edit/', views.UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-profile'),
]
