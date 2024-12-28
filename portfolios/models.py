import uuid
from django.db import models
from users.models import PofoloUser
from projects.models import Project

class Portfolio(models.Model):
    writer = models.ForeignKey(PofoloUser, on_delete=models.CASCADE, related_name="portfolios")
    title = models.CharField(max_length=50, blank=False, null=False)
    major_field = models.CharField(max_length=100, blank=False, null=False) #대분류 - plan, design, develop
    sub_field = models.CharField(max_length=100, blank=False, null=False) #소분류 
    description = models.TextField(max_length=200, blank=False, null=False)
    skills = models.TextField(blank=False, null=False)
    experiences = models.JSONField(default=list)
    related_projects = models.ManyToManyField(Project, related_name="portfolios")  # 연결된 프로젝트들
    invite_url = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # 초대용 랜덤 URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    views = models.IntegerField(default=0) #조회수 
    username = models.CharField(max_length=50, blank=False, null=False, default="Unknown User")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'portfolios'
