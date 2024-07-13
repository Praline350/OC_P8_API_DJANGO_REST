from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from projects.models import Project, Contributor, Issue, Comment
from projects.serializers import ProjectListSerializer, ProjectDetailSerializer, ContributorSerializer, CommentSerializer, IssueDetailSerializer, IssueListSerializer
from projects.permissions import IsAuthor, IsProjectContributor


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
            self.permission_classes = [IsAuthenticated, IsProjectContributor]
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
    

class IssueViewset(MultipleSerializerMixin ,ModelViewSet):
    serializer_class = IssueListSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Issue.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(id=project_id)
        author = Contributor.objects.get(user=self.request.user, project=project)
        serializer.save(author=author, project=project)

class CommentViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Comment.objects.all()
    


