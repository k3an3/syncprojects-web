from django.urls import path

from . import views

app_name = 'todo'
urlpatterns = [
    path('list/<int:project>/', views.TodoListView.as_view(), name='list-todo'),
    path('new/<int:project>/', views.TodoCreateView.as_view(), name='create-todo'),
    path('edit/<int:pk>/', views.TodoUpdateView.as_view(), name='update-todo'),
    path('delete/<int:pk>/', views.TodoDeleteView.as_view(), name='delete-todo'),
]
