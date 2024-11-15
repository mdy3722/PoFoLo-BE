from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Portfolio
from .serializers import PortfolioListSerializer, PortfolioDetailSerializer

# 포트폴리오 리스트 조회
class PortfolioListView(generics.ListAPIView):
    serializer_class = PortfolioListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(writer=self.request.user)

# 포트폴리오 상세내용 조회
class PortfolioDetailView(generics.RetrieveAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioDetailSerializer
    lookup_field = 'pk'

# 포트폴리오 생성
class PortfolioCreateView(generics.CreateAPIView):
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

# 포트폴리오 수정/삭제
class ProjectUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(writer=self.request.user)

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