from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Project, TemporaryImage
from .serializers import ProjectListSerializer, ProjectDetailSerializer
from django.contrib.sessions.backends.db import SessionStore


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

# - 프로젝트 생성
class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user) #해당 사용자를 작성자(writer)로 지정


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

# - 프로젝트 수정/삭제
class ProjectUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()





"""link의 title 반환 로직"""
class LinkTitleView(APIView):
    permission_classes = [AllowAny]

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