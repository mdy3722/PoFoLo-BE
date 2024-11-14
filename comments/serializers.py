from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'writer', 'project', 'commented_at', 'text', 'parent_comment']
        read_only_fields = ['writer', 'commented_at'] # 작성자, 작성시간 수정 불가
    
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data['writer'] = request.writer
        return super().create(validated_data)
