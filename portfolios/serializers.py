from rest_framework import serializers
from .models import Portfolio
from projects.models import Project

class PortfolioListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id','title', 'thumbnail', 'created_at']

    def get_thumbnail(self, obj):
        first_project = obj.related_projects.first()

        if not first_project or not hasattr(first_project, 'project_img'):
            return None

        project_img = first_project.project_img
        return project_img[0] if project_img else None


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