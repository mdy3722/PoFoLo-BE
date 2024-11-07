from django.urls import path
from .views import (
   ProjectListView
#    , ProjectDetailView, ProjectCreateView,
    # MyProjectsView, ProjectUpdateDeleteView, MyProjectsView, LikeProjectView, CommentProjectView
)

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),
    # path('project/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    # path('project/', ProjectCreateView.as_view(), name='project-create'),
    # path('project/<int:pk>/', ProjectUpdateDeleteView.as_view(), name='project-update-delete'),
    # path('users/project/myproject/', MyProjectsView.as_view(), name='my-projects'),
    # path('users/project/liked/', LikeProjectView.as_view(), name='liked-projects'),
    # path('users/project/commented/', CommentProjectView.as_view(), name='commented-projects'),
]
