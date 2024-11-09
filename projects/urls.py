from django.urls import path
from .views import (
   ProjectListView, ProjectDetailView,
#   ProjectCreateView, MyProjectsView, ProjectUpdateDeleteView, MyProjectsView, LikeProjectView, CommentProjectView
)

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    # path('projects/', ProjectCreateView.as_view(), name='project-create'),
    # path('projects/<int:pk>/', ProjectUpdateDeleteView.as_view(), name='project-update-delete'),
    # path('users/projects/myproject/', MyProjectsView.as_view(), name='my-projects'),
    # path('users/projects/liked/', LikeProjectView.as_view(), name='liked-projects'),
    # path('users/projects/commented/', CommentProjectView.as_view(), name='commented-projects'),
]
