from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('login/', login),
    path('register/', register),
    path('profile/<int:user_id>/', manage_profile, name='profile'),
    path('logout/', logout),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신 엔드포인트
]