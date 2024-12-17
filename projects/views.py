from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Project, Comment, Like, PofoloUser
from .serializers import ProjectListSerializer, ProjectDetailSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from utils.s3_utils import s3_file_upload_by_file_data
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser


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

# - 프로젝트 세부내용 조회
class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 인증 없이 접근 가능

    def get_object(self):
        project = super().get_object()
        project.views += 1 #GET 요청시 조회수 증가 
        project.save()
        return project

    def perform_update(self, serializer):
        serializer.save()

class ProjectCreateAndImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # JSON + 파일 처리

    def post(self, request):
        serializer = ProjectDetailSerializer(data=request.data, context={"request": request})
        
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)
        
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
        project = get_object_or_404(Project, id=project_id)  # 좋아요를 누를 프로젝트
        like_instance = Like.objects.filter(user=user, project=project).first()

        if like_instance: #좋아요 취소
            like_instance.delete()
            project.liked_count -= 1
            project.save()
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        else:
            Like.objects.create(user=user, project=project) #좋아요 추가
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
class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """
        특정 프로젝트의 모든 댓글과 답글을 반환
        """
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # 부모 댓글만 가져오기, 답글은 Serializer에서 처리
        comments = Comment.objects.filter(project=project, parent_comment__isnull=True).prefetch_related('replies')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                parent_comment = Comment.objects.get(id=parent_comment_id, project=project)
                # 답글에 대한 답글 방지
                if parent_comment.parent_comment is not None:
                    return Response({"error": "Replies to replies are not allowed"}, status=status.HTTP_400_BAD_REQUEST)
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # 댓글 데이터를 시리얼라이저로 전달
        pofolo_user = get_object_or_404(PofoloUser, user=self.request.user)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=pofolo_user, project=project, parent_comment=parent_comment)
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
        if comment.writer.user != request.user:  # PofoloUser의 user 필드와 비교
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
        return Project.objects.filter(writer=self.request.user)

# - 좋아요한 프로젝트 조회
class LikedProjectView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        liked_projects = Like.objects.filter(user=self.request.user).values_list('project', flat=True)
        return Project.objects.filter(id__in=liked_projects)

# - 코멘트한 프로젝트 조회
class CommentedProjectView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        commented_projects = Comment.objects.filter(writer=self.request.user).values_list('project', flat=True)
        return Project.objects.filter(id__in=commented_projects)