from rest_framework import serializers
from .models import Portfolio
from projects.models import Project

class PortfolioListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title', 'thumbnail', 'created_at']

    def get_thumbnail(self, obj):
        #FIX - None 대신 디폴트 이미지 url 첨부해야됨. 
        return obj.image_urls[0] if obj.image_urls else None 


class PortfolioDetailSerializer(serializers.ModelSerializer):
    related_projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'major_field', 'sub_field', 'description',
            'skills', 'experiences', 'related_projects', 'invite_url', 'created_at', 
            'updated_at', 'is_public', 'views'
        ]
        read_only_fields = ['writer', 'created_at', 'updated_at', 'views', 'invite_url']  # 읽기 전용 필드