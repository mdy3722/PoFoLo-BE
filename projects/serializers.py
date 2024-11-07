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

class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['writer', 'project_id', 'title', 'description', 'major_field', 'sub_field','tags', 'skills', 'links', 
                'image_urls', 'created_at', 'is_public', 'liked_count', 'comment_count', 'views']
    
    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("Description is required.")
        return value

    def validate_field(self, value):
        if not value:
            raise serializers.ValidationError("Field is required.")
        return value

    def validate_picture_urls(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("You can upload a maximum of 10 images!!")
        return value
