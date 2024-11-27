from rest_framework import serializers
from .models import PofoloUser, User
from django.conf import settings
from utils import s3_utils

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = PofoloUser
    exclude = ['user']

    def update(self, instance, validated_data):
        # `profile_img` 필드가 있는 경우 처리
        profile_img_file = self.context['request'].FILES.get('profile_img', None)
        if profile_img_file:
            instance.profile_img = s3_utils.s3_file_upload_by_file_data(
                upload_file=profile_img_file,
                region_name = settings.AWS_S3_REGION_NAME,
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME,
                bucket_path=f"user/profile_images/{instance.id}"
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance