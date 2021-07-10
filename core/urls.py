from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:pk>/unsubscribe/', views.ProjectUnsubscribeView.as_view(), name='project-unsubscribe'),
    path('projects/<int:pk>/songs/create/', views.SongCreateView.as_view(), name='song-create'),
    path('projects/<int:proj>/songs/<int:song>/', views.SongDetailView.as_view(), name='song-detail'),
    path('projects/<int:proj>/songs/<int:song>/edit/', views.SongUpdateView.as_view(), name='song-update'),
    path('projects/<int:proj>/songs/<int:song>/delete/', views.SongDeleteView.as_view(), name='song-delete'),
    path('projects/<int:proj>/songs/<int:song>/clear_peaks/', views.ClearSongPeaksView.as_view(),
         name='song-clear-peaks'),
    path('projects/<int:pk>/albums/create/', views.AlbumCreateView.as_view(), name='album-create'),
    path('projects/<int:proj>/albums/<int:album>/edit/', views.AlbumUpdateView.as_view(), name='album-update'),
    path('projects/<int:proj>/albums/<int:album>/delete/', views.AlbumDeleteView.as_view(), name='album-delete'),
    path('projects/<int:proj>/songs/<int:song>/regen_url/', views.RegenSongURLView.as_view(),
         name='song-regen-url'),
    path('projects/<int:proj>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
    path('projects/<int:proj>/songs/<int:song>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
]
