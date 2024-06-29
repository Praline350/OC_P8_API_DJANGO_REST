from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from projects.models import Project, Contributor
from projects.serializers import ProjectListSerializer, ProjectDetailSerializer, ContributorSerializer
from projects.permissions import IsAuthor, IsContributor


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy'] and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectViewset(MultipleSerializerMixin ,ModelViewSet):
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'create']:
            self.permission_classes = [AllowAny]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsAuthenticated, IsContributor]
        else:  # ['update', 'partial_update', 'destroy']
            self.permission_classes = [IsAuthenticated, IsAuthor]
        return super().get_permissions()

    def get_queryset(self):
        return Project.objects.all()
    

class ContributorViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Contributor.objects.all()
