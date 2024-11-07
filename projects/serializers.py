from rest_framework import serializers
from .models import Project, Like, Comment

class ProjectListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['writer', 'title', 'major_field', 'sub_field',
        'liked_count', 'comment_count', 'thumbnail', 'created_at']

    def get_thumbnail(self, obj):
        #FIX - None 대신 디폴트 이미지 url 첨부해야됨. 
        return obj.image_urls[0] if obj.image_urls else None 