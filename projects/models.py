from django.db import models
from django.core.exceptions import ValidationError
from users.models import PofoloUser

class Project(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(max_length=200, blank=False, null=False)
    major_field = models.CharField(max_length=100, blank=False, null=False) #대분류 - plan, design, develop + CharField에 max_length 설정 필수!
    sub_field = models.CharField(max_length=100, blank=False, null=False) #소분류 
    tags = models.JSONField(default=list)
    skills = models.TextField(max_length=200, blank=True, null=True)
    links = models.JSONField()
    project_img = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.CharField(max_length=10, default="fault")#BooleanField(default=True)
    liked_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    views = models.IntegerField(default=0) #조회수 
    writer = models.ForeignKey(PofoloUser, on_delete=models.CASCADE)

    def clean(self):
        if len(self.project_img) > 10:
            raise ValidationError("uploaded more than 10 images.")
    
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'projects'

# 이미지 관리 class
class TemporaryImage(models.Model):
    session_key = models.CharField(max_length=255, unique=False, null=False)  # 사용자 고유 세션 키
    image_url = models.URLField(null=False)  # S3에 업로드된 URL
    created_at = models.DateTimeField(auto_now_add=True)  # 정리 스케줄링용

class Like(models.Model):
    user = models.ForeignKey(PofoloUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    writer = models.ForeignKey(PofoloUser, on_delete=models.CASCADE, related_name="comments")  # 댓글 작성자
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    commented_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()  
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies") # 답글은 부모 댓글과 연결 됨. 일종의 상속 개념

    def __str__(self):
        return f"{self.writer.nickname} - {self.text[:20]}"