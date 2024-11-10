from django.urls import path
from .views import CommentCreateView

urlpatterns = [
    path('projects/<int:project_id>/comments',CommentCreateView.as_view(), name='project-comment-create')
]