from django.urls import path
from .views import PortfolioListView, PortfolioDetailView, PortfolioCreateView, ProjectUpdateDeleteView, PortfolioInviteView

urlpatterns = [
    path('', PortfolioListView.as_view(), name='portfolio-list'),  # 리스트 조회
    path('<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),  # 상세 조회
    path('create/', PortfolioCreateView.as_view(), name='project-create'),  # 생성
    path('<int:pk>/', ProjectUpdateDeleteView.as_view(), name='project-detail'), #수정 및 삭제
    path('invite/<uuid:invite_url>/', PortfolioInviteView.as_view(), name='portfolio-invite'),  # 초대 URL로 조회
]