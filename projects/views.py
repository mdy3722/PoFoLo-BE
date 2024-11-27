from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Project, TemporaryImage, Comment, Like, PofoloUser
from .serializers import ProjectListSerializer, ProjectDetailSerializer, CommentSerializer
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError 
from django.shortcuts import get_object_or_404
from utils.s3_utils import s3_file_upload_by_file_data
from django.conf import settings


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
        user_id = self.kwargs.get('user_id')  # URL 경로에서 user_id를 가져옴
        field = self.request.query_params.get('field')  # major_field 필터링

        if user_id:
            queryset = queryset.filter(writer__id=user_id)
        if field:
            queryset = queryset.filter(major_field=field)

        return queryset

# - 프로젝트 세부내용 조회/수정/삭제
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        project = super().get_object()
        project.views += 1 #GET 요청시 조회수 증가 
        project.save()
        return project

    def perform_update(self, serializer):
        serializer.save()

# - 프로젝트 생성
class ProjectCreateView(APIView):
    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            return Response({"error": "세션이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            pofolo_user = get_object_or_404(PofoloUser, user=self.request.user)
            project = serializer.save(writer=pofolo_user)

            # TemporaryImage에서 이미지 가져와 연결
            temporary_images = TemporaryImage.objects.filter(session_key=session_key)
            project.project_img = [img.image_url for img in temporary_images[:10]]  # 최대 10개
            project.save()

            # 임시 이미지 삭제
            temporary_images.delete()

            return Response({
                "message": "프로젝트 생성 성공",
                "project": ProjectDetailSerializer(project).data
            }, status=status.HTTP_201_CREATED)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# - 프로젝트 이미지 추가
class ProjectImageUploadView(APIView):
    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        image_files = request.FILES.getlist('project_img')
        if not image_files:
            return Response({"error": "이미지가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_urls = []
        for image_file in image_files: 
            uploaded_url = s3_file_upload_by_file_data(
                upload_file=image_file,
                region_name=settings.AWS_S3_REGION_NAME,
                bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                bucket_path=f"project/temp_images/{session_key}"
            )
            if uploaded_url:
                # TemporaryImage에 업로드 정보 저장
                TemporaryImage.objects.create(session_key=session_key, image_url=uploaded_url)
                uploaded_urls.append(uploaded_url)

            if not uploaded_url:
                return Response({"error": "이미지 업로드 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "이미지 업로드 성공",
            "image_urls": uploaded_urls,
            #"temp_image_id": temp_image.id
        }, status=status.HTTP_201_CREATED)

class ProjectImageManageView(APIView):
    def patch(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        pofolo_user = get_object_or_404(PofoloUser, user=self.request.user)
        # 권한 체크
        if pofolo_user != project.writer:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 기존 이미지 가져오기
        current_images = project.project_img or []

        # 새 이미지 추가 처리
        new_images = request.FILES.getlist('new_images', [])
        for image_file in new_images:
            if len(current_images) >= 10:  # 최대 10개 제한
                return Response({"error": "이미지는 최대 10개까지만 업로드할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            uploaded_url = s3_file_upload_by_file_data(
                upload_file=image_file,
                region_name=settings.AWS_S3_REGION_NAME,
                bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                bucket_path=f"project/images/{project.writer.id}"
            )
            if uploaded_url:
                current_images.append(uploaded_url)

        # 삭제 이미지 처리
        delete_images = request.data.get('delete_images', [])
        current_images = [img for img in current_images if img not in delete_images]

        # 변경된 이미지 저장
        project.project_img = current_images
        project.save()

        serializer = ProjectDetailSerializer(project)
        return Response({
            "message": "이미지 수정 성공",
            "project": serializer.data
        }, status=status.HTTP_200_OK)

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