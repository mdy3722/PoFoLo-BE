from typing_extensions import Required
from django.db.models.fields import related
from rest_framework import serializers
from .models import Portfolio
from projects.models import Project
from utils.s3_utils import generate_presigned_url

class PortfolioListSerializer(serializers.ModelSerializer):
    related_projects = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()  # Custom 처리


    class Meta:
        model = Portfolio
        fields = ['id', 'writer', 'title', 'thumbnail', 'created_at', 'related_projects']

    def get_related_projects(self, obj):
        related_project_ids = self.context['request'].data.get('related_projects', [])

        if related_project_ids:
            ordered_projects = sorted(
                obj.related_projects.filter(id__in=related_project_ids),
                key=lambda project: related_project_ids.index(project.id)
            )
            return [project.id for project in ordered_projects]
        
        return [project.id for project in obj.related_projects.all()]

    def get_thumbnail(self, obj):
        related_projects = obj.related_projects.all()
        for related_project in related_projects:
            if related_project.project_img:
                first_image_url = related_project.project_img[0]
                try:
                    return generate_presigned_url(first_image_url)
                except ValueError:
                    continue  # Presigned URL 생성 실패 시 다음 프로젝트로 이동
        return None

class PortfolioDetailSerializer(serializers.ModelSerializer):
    related_projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'writer', 'title', 'major_field', 'sub_field', 'description',
            'skills', 'experiences', 'related_projects', 'invite_url', 'created_at', 
            'updated_at', 'is_public', 'views', 'username'
        ]
        read_only_fields = ['writer', 'created_at', 'updated_at', 'views', 'invite_url']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        related_project_ids = self.context['request'].data.get('related_projects', [])

        if related_project_ids:
            ordered_projects = sorted(
                instance.related_projects.filter(id__in=related_project_ids),
                key=lambda project: related_project_ids.index(project.id)
            )
            representation['related_projects'] = [project.id for project in ordered_projects]
        else:
            representation['related_projects'] = [project.id for project in instance.related_projects.all()]

        return representation