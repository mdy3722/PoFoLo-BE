from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('pofolo/users/login/', login),
    path('pofolo/users/register/', register),
    path('pofolo/users/profile/<int:user_id>/', manage_profile, name='profile'),
    path('pofolo/users/logout/', logout),
    path('pofolo/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신 엔드포인트
]