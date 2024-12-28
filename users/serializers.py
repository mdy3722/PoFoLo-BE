from rest_framework import serializers
from .models import PofoloUser
from django.conf import settings
from django.shortcuts import get_object_or_404
from utils.s3_utils import generate_presigned_url, s3_file_upload_by_file_data

class UserSerializer(serializers.ModelSerializer):
    profile_img_url = serializers.SerializerMethodField()  # Pre-signed URL 반환용 필드

    class Meta:
        model = PofoloUser
        read_only_fields = ['id', 'kakao_id', 'profile_img']
        exclude = ['user']

    def get_profile_img_url(self, obj):
        if not obj.profile_img:
            return None
        return generate_presigned_url(obj.profile_img)