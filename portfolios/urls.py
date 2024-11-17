from django.urls import path
from .views import PortfolioListView, PortfolioDetailView, PortfolioCreateView, PortfolioInviteView

urlpatterns = [
    path('', PortfolioListView.as_view(), name='portfolio-list'),  # 리스트 조회
    path('<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),  # 상세 조회/수정/삭제
    path('create/', PortfolioCreateView.as_view(), name='portfolio-create'),  # 생성
    path('invite/<uuid:invite_url>/', PortfolioInviteView.as_view(), name='portfolio-invite'),  # 초대 URL로 조회
    path('watch/<int:user_id>/', PortfolioListView.as_view(), name='portfolio-list') #다른사람 포폴 리스트 조회
]