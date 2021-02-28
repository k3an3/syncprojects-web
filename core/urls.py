from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:pk>/songs/create/', views.SongCreateView.as_view(), name='song-create'),
    path('projects/<int:proj>/songs/<int:song>', views.SongDetailView.as_view(), name='song-detail'),
    path('projects/<int:proj>/songs/<int:song>/delete/', views.SongDeleteView.as_view(), name='song-delete'),
    path('projects/<int:proj>/songs/<int:song>/clear_peaks/', views.ClearSongPeaksView.as_view(),
         name='song-clear-peaks'),
]
