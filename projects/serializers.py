from rest_framework import serializers
from .models import Project, Comment, PofoloUser
from django.conf import settings
from django.shortcuts import get_object_or_404
from utils.s3_utils import s3_file_upload_by_file_data

class ProjectListSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.nickname')
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'writer', 'writer_name', 'title', 'major_field', 'sub_field',
        'liked_count', 'comment_count', 'thumbnail', 'created_at']

    def get_thumbnail(self, obj):
        return obj.project_img[0] if obj.project_img else None 

class ProjectDetailSerializer(serializers.ModelSerializer):
    
    project_img = serializers.ListField(
        child=serializers.URLField(),
        read_only=True
    )

    class Meta:
        model = Project
        fields = ['id', 'writer', 'title', 'description', 'major_field', 'sub_field','tags', 'skills', 'links', 
                'project_img', 'created_at', 'is_public', 'liked_count', 'comment_count', 'views']
        read_only_fields = ['id', 'writer', 'created_at', 'liked_count', 'comment_count', 'views']

    def get_object(self):
        project = super().get_object()
        project.views += 1 #GET 요청시 조회수 증가 
        project.save()
        return project
    
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
    
    def create(self, validated_data):
        request = self.context['request']
        writer = get_object_or_404(PofoloUser, user=request.user)
        project_img_files = request.FILES.getlist('project_img')
        project = Project.objects.create(writer=writer, **validated_data)
        
        # S3 업로드 로직
        uploaded_urls = []
        for img_file in project_img_files:
            uploaded_url = s3_file_upload_by_file_data(
                upload_file=img_file,
                region_name=settings.AWS_S3_REGION_NAME,
                bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                bucket_path=f"project/{project.id}"
            )
            print(f"Uploaded URL: {uploaded_url}")
            if uploaded_url:
                uploaded_urls.append(uploaded_url)
        print(f"Uploaded URLs: {uploaded_urls}")
        project.project_img = uploaded_urls
        project.save()
        return project

    def update(self, instance, validated_data):
        request = self.context['request']
        image_files = request.FILES.getlist('project_img')  # 새로운 이미지 업로드 요청 확인

        if image_files:
            image_urls = instance.project_img or []
            for image_file in image_files[:10 - len(image_urls)]:  # 기존 이미지와 합쳐 최대 10개 제한
                uploaded_url = s3_file_upload_by_file_data(
                    upload_file=image_file,
                    region_name=settings.AWS_S3_REGION_NAME,
                    bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                    bucket_path=f"project/images/{instance.writer.id}"
                )
                if uploaded_url:
                    image_urls.append(uploaded_url)
            validated_data['project_img'] = image_urls

        # 다른 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

"""댓글"""
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()  # 답글 필드 추가

    class Meta:
        model = Comment
        fields = ['id', 'writer', 'project', 'commented_at', 'text', 'parent_comment', 'replies']
        read_only_fields = ['writer', 'commented_at', 'project'] # 작성자, 작성시간 수정 불가

    def get_replies(self, obj):
        """
        부모 댓글에 연결된 답글 목록을 직렬화합니다.
        """
        if obj.replies.exists():  # replies는 related_name을 사용해 연결됨
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
