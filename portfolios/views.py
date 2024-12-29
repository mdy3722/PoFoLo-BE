from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Portfolio, PofoloUser, Project
from .serializers import PortfolioListSerializer, PortfolioDetailSerializer
from utils.s3_utils import generate_presigned_url

# 포트폴리오 리스트 조회
class PortfolioListView(generics.ListAPIView):
    serializer_class = PortfolioListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            queryset = Portfolio.objects.filter(writer__id=user_id, is_public=True)
        else:
            queryset = Portfolio.objects.filter(writer=user)
        return queryset

# 포트폴리오 상세내용 조회/수정/삭제 
class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        portfolio = super().get_object()
        portfolio.views += 1 #GET 요청시 조회수 증가 
        portfolio.save()
        return portfolio

    def perform_update(self, serializer):
        serializer.save()

# 포트폴리오 생성
class PortfolioCreateView(generics.CreateAPIView):
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = get_object_or_404(PofoloUser, user=self.request.user)
        related_projects = self.request.data.get('related_projects', [])
        thumbnail_url = None

        # # 썸네일 이미지 URL 설정
        for project_id in related_projects:
            related_project = Project.objects.filter(id=project_id).first()
            if related_project and related_project.project_img:
                first_image_url = related_project.project_img[0]
                try:
                    thumbnail_url = generate_presigned_url(first_image_url)
                except ValueError:
                    thumbnail_url = ""

        # Portfolio 객체 저장 (id가 생성됨)
        portfolio = serializer.save(writer=user, thumbnail=thumbnail_url)

        # Many-to-Many 관계 추가: 포트폴리오가 저장된 후에 추가해야 함
        for project_id in related_projects:
            related_project = Project.objects.filter(id=project_id).first()
            if related_project:
                portfolio.related_projects.add(related_project)

        # portfolio.save()를 호출하여 데이터베이스에 반영
        portfolio.save()


# 포트폴리오 초대 URL 조회
class PortfolioInviteView(generics.RetrieveAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.AllowAny]  # 인증 없이 접근 가능

    def get_object(self):
        invite_url = self.kwargs['invite_url']
        portfolio = get_object_or_404(Portfolio, invite_url=invite_url)
        
        portfolio.views += 1 #인사팀 URL로 접근시 조회수 증가
        portfolio.save(update_fields=['views'])
        
        return portfolio