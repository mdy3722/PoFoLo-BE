from django.urls import path
from .views import (
   ProjectListView, ProjectDetailView,
   ProjectCreateView, ProjectUpdateDeleteView, ProjectImageUploadView,
   LinkTitleView,
#   MyProjectsView, LikeProjectView, CommentProjectView
)
from comments.views import CommentCreateView

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-list'),#프로젝트 리스트 조회
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'), # 프로젝트 세부사항 조회
    # 아래 url이 프로젝트 조회 url과 일치하여 오류가 날 듯 - 하나의 view에서 두 개의 request(GET, POST)로 분기하거나
    # /pofolo/projects/create와 같이 수정이 필요할 듯!!
    path('', ProjectCreateView.as_view(), name='project-create'),  # 프로젝트 생성
    path('upload-images/', ProjectImageUploadView.as_view(), name='project-upload-images'), # 이미지 추가    
    path('<int:pk>/', ProjectUpdateDeleteView.as_view(), name='project-detail'), #수정 및 삭제

    
    # path('users/projects/myproject/', MyProjectsView.as_view(), name='my-projects'),
    # path('users/projects/liked/', LikeProjectView.as_view(), name='liked-projects'),
    # path('users/projects/commented/', CommentProjectView.as_view(), name='commented-projects'),

    path('<int:project_id>/comments/',CommentCreateView.as_view(), name='project-comment-create'), # 댓글(및 답글) 작성
    path('links/', LinkTitleView.as_view(), name='link-title')   # 링크를 받아 <title> 태그값을 반환

]
