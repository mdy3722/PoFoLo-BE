from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Project, TemporaryImage, Comment, Like, PofoloUser
from .serializers import ProjectListSerializer, ProjectDetailSerializer, CommentSerializer
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError 
from django.shortcuts import get_object_or_404



"""링크 title 태그 반환을 위한 import"""
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse

# Main Page
# - 프로젝트 목록 조회
class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(is_public=True)
        field = self.request.query_params.get('field') #filtering with major_field 
        if field:
            queryset = queryset.filter(major_field=field)
        return queryset

# - 프로젝트 세부내용 조회/수정/삭제
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        serializer.save()

# - 프로젝트 생성
class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            pofolo_user = get_object_or_404(PofoloUser, user=self.request.user)
            serializer.save(writer=pofolo_user) # writer를 PofoloUser로 설정

        except AttributeError:
            raise ValidationError("The user does not have a linked PofoloUser instance.")

# - 프로젝트 이미지 추가
class ProjectImageUploadView(APIView):
    def post(self, request):
        session_key = request.session.session_key or request.session.create()  # 세션 키 생성
        image_urls = request.data.get('picture_urls', [])

        if len(image_urls) > 10:
            return Response({"error": "You can upload a maximum of 10 images."}, status=status.HTTP_400_BAD_REQUEST)

        for image_url in image_urls:
            TemporaryImage.objects.create(image_url=image_url, session_key=session_key)

        return Response({"message": "Images uploaded successfully.", "session_key": session_key}, status=status.HTTP_201_CREATED)

# - 좋아요 누르기
class LikeProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        project = get_object_or_404(Project, id=project_id)

        like_instance = Like.objects.filter(user=user, project=project).first()
        if like_instance:
            # 이미 좋아요가 눌러진 상태
            like_instance.delete()
            project.liked_count -= 1
            project.save()
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        else:
            # 좋아요가 눌러지지 않은 상태
            Like.objects.create(user=user, project=project)
            project.liked_count += 1
            project.save()
            return Response({"message": "Like added"}, status=status.HTTP_201_CREATED)
    
"""link의 title 반환 로직"""
class LinkTitleView(APIView):
    permission_classes = [AllowAny]    # AllowAny는 로컬테스트용. 나중에 IsAuthenticated으로 수정 해야 함

    def post(self, request):
        link = request.data.get('link')
        
        if not link:
            return JsonResponse({'error': 'URL is required.'}, status=400)
        
        try:
            # URL로 HTML 가져오기
            response = requests.get(link)
            response.raise_for_status()  # HTTP 오류 확인

            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else 'No Title Found'

            return JsonResponse({'title': title})
        
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400)

"""댓글 및 답글 작성하기"""
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        # 프로젝트 인스턴스를 가져옴
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # 부모 댓글이 있는지 확인 (답글 작성)
        parent_comment_id = request.data.get('parent_comment')  # 클라이언트가 어떤 댓글에 대한 답글을 작성할 경우 부모 댓글의 id를 포함해 서버로 요청
        parent_comment = None   # 부모 댓글 id가 없으면 부모 댓글 객체를 none으로 유지
        if parent_comment_id:   # 답글이라면
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, project=project)  # 프론트엔드에서 받은 부모 댓글 id를 조회해 부모 댓글 객체 할당
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # 댓글 데이터를 시리얼라이저로 전달
        serializer = CommentSerializer(
            data=request.data,
            context={
                'request': request,  # request 객체 전달
            }
        )
        if serializer.is_valid():
            user = get_object_or_404(PofoloUser, user=request.user)
            serializer.save(writer=user, project=project, parent_comment=parent_comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""댓글 삭제 기능"""
class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated] 

    def delete(self, request, comment_id):
        # 댓글 인스턴스 가져오기
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # 요청한 사용자가 댓글 작성자인지 확인
        if comment.writer != request.user:
            return Response({"error": "You do not have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        # 댓글 삭제
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# MyPage
# - 내 프로젝트 조회
class MyProjectsView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        return Project.objects.filter(writer=user)

# - 좋아요한 프로젝트 조회
class LikedProjectView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        liked_projects = Like.objects.filter(user=user).values_list('project', flat=True)
        return Project.objects.filter(id__in=liked_projects)

# - 코멘트한 프로젝트 조회
class CommentedProjectView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        commented_projects = Comment.objects.filter(writer=user).values_list('project', flat=True)
        return Project.objects.filter(id__in=commented_projects)