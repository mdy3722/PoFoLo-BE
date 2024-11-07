from django.db import models
from django.contrib.auth.models import User

def get_default_availability():
    return ["제안 받지 않음"]

# Create your models here.
class PofoloUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pofolo_user', null=True)  # 기본 User 모델과 연결
    kakao_id = models.CharField(max_length=50, unique=True)  # 카카오 ID를 고유 식별자로 사용 -> 기존 회원인지, 신규 회원인지 확인 용
    nickname = models.CharField(max_length=50, unique=True)   
    education = models.CharField(max_length=50, null=False, blank=False)   # 학력
    education_is_public = models.BooleanField(default=True)  # 학력 공개 디폴트
    main_field = models.CharField(max_length=10, choices=[('plan', 'plan'), ('design', 'design'), ('develop', 'develop')], default='기획')
    phone_num = models.CharField(max_length=15, blank=True, null=True)
    phone_num_is_public = models.BooleanField(default=False)  # 전화번호 비공개 디폴트
    email = models.EmailField(blank=True, null=True)
    email_is_public = models.BooleanField(default=False)  # 이메일 비공개 디폴트
    introduction = models.TextField(blank=True, null=True)
    links = models.JSONField(blank=True, null=True)  
    availability = models.JSONField(null=True, blank=True, default=get_default_availability)  

