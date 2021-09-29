from django.urls import path

from . import views

app_name = 'snippets'
urlpatterns = [
    path('list/<int:project>/', views.SnippetListView.as_view(), name='list-project'),
    path('list/<int:song>/', views.SnippetListView.as_view(), name='list-song'),
    path('add/<int:project>/', views.SnippetListView.as_view(), name='new-project'),
    path('add/<int:song>/', views.SnippetListView.as_view(), name='new-song'),
]
