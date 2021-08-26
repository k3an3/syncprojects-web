from django.urls import path

from comments import views

app_name = 'comments'
urlpatterns = [
    path('projects/<int:proj>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
    path('projects/<int:proj>/songs/<int:song>/comment/', views.CommentCreateView.as_view(),
         name='comment-create'),
    path('projects/<int:proj>/songs/<int:song>/comment/<int:pk>/delete/', views.CommentDeleteView.as_view(),
         name='comment-delete'),
    path('projects/<int:proj>/comment/<int:pk>/delete/', views.CommentDeleteView.as_view(),
         name='comment-delete'),
]
