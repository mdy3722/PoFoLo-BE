from typing_extensions import Required
from rest_framework import serializers
from .models import Portfolio
from projects.models import Project

class PortfolioListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    related_projects = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id','title', 'thumbnail', 'created_at', 'related_projects']

    def get_thumbnail(self, obj):
        related_project_ids = self.context['request'].data.get('related_projects', [])
        
        for project_id in related_project_ids:
            related_project = obj.related_projects.filter(id=project_id).first()
            if related_project and related_project.project_img:
                return related_project.project_img[0]
        return None

    def get_related_projects(self, obj):
        related_project_ids = self.context['request'].data.get('related_projects', [])

        if related_project_ids:
            ordered_projects = sorted(
                obj.related_projects.filter(id__in=related_project_ids),
                key=lambda project: related_project_ids.index(project.id)
            )
            return [project.id for project in ordered_projects]
        
        return [project.id for project in obj.related_projects.all()]

class PortfolioDetailSerializer(serializers.ModelSerializer):
    related_projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'major_field', 'sub_field', 'description',
            'skills', 'experiences', 'related_projects', 'invite_url', 'created_at', 
            'updated_at', 'is_public', 'views'
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