from rest_framework import serializers
from .models import PofoloUser
from django.conf import settings
from django.shortcuts import get_object_or_404
from utils.s3_utils import generate_presigned_url, s3_file_upload_by_file_data

class UserSerializer(serializers.ModelSerializer):
    profile_img_url = serializers.SerializerMethodField()  # Pre-signed URL 반환용 필드
    education_is_public = serializers.BooleanField()  # 불리언 값으로 처리
    phone_num_is_public = serializers.BooleanField()  # 불리언 값으로 처리
    email_is_public = serializers.BooleanField()  # 불리언 값으로 처리

    class Meta:
        model = PofoloUser
        read_only_fields = ['id', 'kakao_id', 'profile_img']
        exclude = ['user']

    def get_profile_img_url(self, obj):
        if not obj.profile_img:
            return None
        return generate_presigned_url(obj.profile_img)
    
    def validate_education_is_public(self, value):
        return self._convert_to_boolean(value)

    def validate_phone_num_is_public(self, value):
        return self._convert_to_boolean(value)

    def validate_email_is_public(self, value):
        return self._convert_to_boolean(value)

    def _convert_to_boolean(self, value):
        """
        문자열로 전달된 값을 불리언 값으로 변환
        """
        if isinstance(value, bool):  # 이미 불리언 값이면 그대로 반환
            return value
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ['true', '1']:
                return True
            elif lower_value in ['false', '0']:
                return False
        raise serializers.ValidationError(f"Invalid boolean value: {value}")