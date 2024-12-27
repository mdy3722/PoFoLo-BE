from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from utils import s3_utils

def get_default_availability():     # 가용성 디폴트 값 반환
    return ["제안 받지 않음"]

# Create your models here.
class PofoloUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pofolo_user', null=True)  # 기본 User 모델과 연결 - 연결 안하면 장고가 유저 관련 로직을 장고 자체 유저에 적용하려고 함
    kakao_id = models.CharField(max_length=50, unique=True)  # 카카오 ID를 고유 식별자로 사용 -> 기존 회원인지, 신규 회원인지 확인 용
    nickname = models.CharField(max_length=50, unique=True)  # 이름(별명)
    education = models.CharField(max_length=50, null=False, blank=False)   # 학력
    education_is_public = models.BooleanField(default=True)  # 학력 공개 디폴트
    main_field = models.CharField(max_length=10, choices=[('plan', 'plan'), ('design', 'design'), ('develop', 'develop')], default='plan')
    phone_num = models.CharField(max_length=15, blank=True, null=True)
    phone_num_is_public = models.BooleanField(default=False)  # 전화번호 비공개 디폴트
    email = models.EmailField(blank=True, null=True)
    email_is_public = models.BooleanField(default=False)  # 이메일 비공개 디폴트
    introduction = models.TextField(blank=True, null=True)
    links = models.JSONField(blank=True, null=True)  
    availability = models.JSONField(null=True, blank=True, default=get_default_availability)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()  # 연결된 User 객체 삭제
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return self.nickname
    
    class Meta:
        db_table = 'users'

