from django.urls import path

from . import views

app_name = 'snippets'
urlpatterns = [
    path('list/<int:project>/', views.SnippetListView.as_view(), name='list-snippets'),
    path('add/<int:project>/', views.SnippetListView.as_view(), name='new-snippet'),
]
