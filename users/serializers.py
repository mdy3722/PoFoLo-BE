from rest_framework import serializers
from .models import PofoloUser
from django.conf import settings
from utils import s3_utils

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = PofoloUser
    exclude = ['user']