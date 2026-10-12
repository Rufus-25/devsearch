from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name="projects"),
    path('project/<uuid:pk>/', views.project, name="project"),

    path('create-project/', views.create_project, name="create-project"),
    path('update-project/<uuid:pk>/', views.update_project, name="update-project"),
    path('delete-project/<uuid:pk>/', views.delete_project, name="delete-project"),

    path('remove-tag/', views.remove_tag, name='remove-tag'),

]
