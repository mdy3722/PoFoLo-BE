from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
#from django.contrib.auth.models import User, Comment

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Project(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(max_length=200, blank=False, null=False)
    major_field = models.CharField(blank=False, null=False) #대분류 - plan, design, develop
    sub_field = models.CharField(blank=False, null=False) #소분류 
    tags = models.ManyToManyField(Tag, related_name="projects")
    skills = models.ManyToManyField(Skill, related_name="projects")
    links = models.JSONField()
    picture_urls = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    liked_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    views = models.IntegerField(default=0) #조회수 
    #writer = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if len(self.image_urls) > 10:
            raise ValidationError("uploaded more than 10 images.")
    
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'projects'


class Like(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateTimeField(auto_now_add=True)