from rest_framework import serializers
from .models import PofoloUser

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = PofoloUser
    exclude = ['user']