from django.urls import path
from .views import (
   ProjectListView, ProjectDetailView,
   ProjectCreateView, ProjectUpdateDeleteView, ProjectImageUploadView,
#   MyProjectsView, LikeProjectView, CommentProjectView
)

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),#프로젝트 리스트 조회
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'), # 프로젝트 세부사항 조회
    path('projects/', ProjectCreateView.as_view(), name='project-create'),  # 프로젝트 생성
    path('projects/upload-images', ProjectImageUploadView.as_view(), name='project-upload-images'), # 이미지 추가    
    path('projects/<int:pk>/', ProjectUpdateDeleteView.as_view(), name='project-detail'), #수정 및 삭제
    # path('users/projects/myproject/', MyProjectsView.as_view(), name='my-projects'),
    # path('users/projects/liked/', LikeProjectView.as_view(), name='liked-projects'),
    # path('users/projects/commented/', CommentProjectView.as_view(), name='commented-projects'),
]
