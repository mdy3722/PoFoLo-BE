from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Project
from .serializers import CommentSerializer

"""댓글 및 답글 작성하기"""
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        # 프로젝트 인스턴스를 가져옴
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # 부모 댓글이 있는지 확인 (답글 작성)
        parent_comment_id = request.data.get('parent_comment')  # 클라이언트가 어떤 댓글에 대한 답글을 작성할 경우 부모 댓글의 id를 포함해 서버로 요청
        parent_comment = None   # 부모 댓글 id가 없으면 부모 댓글 객체를 none으로 유지
        if parent_comment_id:   # 답글이라면
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, project=project)  # 프론트엔드에서 받은 부모 댓글 id를 조회해 부모 댓글 객체 할당
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # 댓글 데이터를 시리얼라이저로 전달
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.writer, project=project, parent_comment=parent_comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
