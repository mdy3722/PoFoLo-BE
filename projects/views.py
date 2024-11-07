from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Project
from .serializers import ProjectListSerializer, ProjectDetailSerializer

# Main Page
# - 프로젝트 목록 조회
class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(is_public=True)
        field = self.request.query_params.get('field') #filtering with major_field 
        if field:
            queryset = queryset.filter(major_field=field)
        return queryset

# - 프로젝트 세부내용 조회
class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_field = 'pk'