from rest_framework import serializers
from .models import Project, Comment, PofoloUser
from django.conf import settings
from django.shortcuts import get_object_or_404
from utils.s3_utils import s3_file_upload_by_file_data, generate_presigned_url

class ProjectListSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.nickname')
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'writer', 'writer_name', 'title', 'major_field', 'sub_field',
        'liked_count', 'comment_count', 'thumbnail', 'created_at']

    def get_thumbnail(self, obj):
        if obj.project_img:
            return generate_presigned_url(obj.project_img[0])
        return None

class ProjectDetailSerializer(serializers.ModelSerializer):
    project_img = serializers.SerializerMethodField()  # pre-signed URL 반환용 필드  
    is_public = serializers.CharField(max_length=10, default="False")  # Keep CharField for the model

    class Meta:
        model = Project
        fields = [
            'id', 'writer', 'title', 'description', 'major_field', 'sub_field', 'skills', 'links',
            'project_img', 'created_at', 'is_public', 'liked_count', 'comment_count', 'views',
        ]
        read_only_fields = ['id', 'writer', 'created_at', 'liked_count', 'comment_count', 'views']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('is_public') == "true":
            representation['is_public'] = True
        elif representation.get('is_public') == "false":
            representation['is_public'] = False
        return representation

    def get_project_img(self, obj):
        """
        `project_img`에 저장된 모든 S3 URL에 대해 Pre-signed URL을 반환.
        """
        if not obj.project_img:
            return []
        return [generate_presigned_url(img_url) for img_url in obj.project_img]

    def create(self, validated_data):
        request = self.context['request']
        writer = get_object_or_404(PofoloUser, user=request.user)
        project_img_files = request.FILES.getlist('project_img')

        if len(project_img_files) > 10:
            raise serializers.ValidationError("최대 10개의 이미지만 업로드할 수 있습니다.")

        # 프로젝트 생성
        project = Project.objects.create(writer=writer, **validated_data)

        # S3 업로드 및 URL 생성
        uploaded_urls = self.upload_images_to_s3(project_img_files, project.id)
        project.project_img = uploaded_urls
        project.save()
        return project

    def update(self, instance, validated_data):
        request = self.context['request']
        project_img_files = request.FILES.getlist('project_img')

        if project_img_files:
            # 기존 이미지와 새로 업로드한 이미지를 합쳐 최대 10개 제한
            existing_images = instance.project_img or []
            if len(existing_images) + len(project_img_files) > 10:
                raise serializers.ValidationError("최대 10개의 이미지만 업로드할 수 있습니다.")

            # 새 이미지 업로드
            new_uploaded_urls = self.upload_images_to_s3(project_img_files, instance.id)
            validated_data['project_img'] = existing_images + new_uploaded_urls

        # 다른 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def upload_images_to_s3(self, image_files, project_id):
        """
        S3에 이미지를 업로드하고 업로드된 URL을 반환합니다.
        """
        uploaded_urls = []
        for img_file in image_files:
            uploaded_url = s3_file_upload_by_file_data(
                upload_file=img_file,
                region_name=settings.AWS_S3_REGION_NAME,
                bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
                bucket_path=f"project/{project_id}"
            )
            if uploaded_url:
                uploaded_urls.append(uploaded_url)
            else:
                raise serializers.ValidationError("S3 업로드에 실패했습니다.")
        return uploaded_urls

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
