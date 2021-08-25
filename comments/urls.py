from django.urls import path

import comments

app_name = 'comments'
urlpatterns = [
    path('projects/<int:proj>/comment/', comments.views.CommentCreateView.as_view(), name='comment-create'),
    path('projects/<int:proj>/songs/<int:song>/comment/', comments.views.CommentCreateView.as_view(),
         name='comment-create'),
    path('projects/<int:proj>/songs/<int:song>/comment/<int:pk>/delete/', comments.views.CommentDeleteView.as_view(),
         name='comment-delete'),
    path('projects/<int:proj>/comment/<int:pk>/delete/', comments.views.CommentDeleteView.as_view(),
         name='comment-delete'),
]
