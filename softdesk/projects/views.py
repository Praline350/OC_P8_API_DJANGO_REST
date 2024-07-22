from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from projects.models import Project, Contributor, Issue, Comment
from projects.serializers import *
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
        match self.action:
            case 'list' | 'create':
                self.permission_classes = [IsAuthenticated]
            case 'retrieve':
                self.permission_classes = [IsAuthenticated, IsProjectContributor]
            case _:
                self.permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthor]
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
    detail_serializer_class = IssueDetailSerializer
    
    def get_permissions(self):
        match self.action:
            case 'list' | 'create' | 'retrieve':
                self.permission_classes = [IsAuthenticated, IsProjectContributor]
            case _:
                self.permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthor]
        return super().get_permissions()

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        return Issue.objects.filter(project_id=project_pk)

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('project_pk')
        project = Project.objects.get(id=project_pk)
        author = Contributor.objects.filter(user=self.request.user, project=project).first()
        serializer.save(author=author, project=project)

class CommentViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CommentSerializer

    def get_permissions(self):
        match self.action:
            case 'list' | 'retrieve':
                self.permission_classes = [IsAuthenticated, IsProjectContributor]
            case _:
                self.permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthor]
        return super().get_permissions()

    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        issue_pk = self.kwargs['issue_pk']
        return Comment.objects.filter(issue_id=issue_pk, issue__project_id=project_pk)

    def perform_create(self, serializer):
        project_pk = self.kwargs['project_pk']
        issue_pk = self.kwargs['issue_pk']
        issue = Issue.objects.get(pk=issue_pk, project_id=project_pk)
        contributor = Contributor.objects.get(user=self.request.user, project_id=project_pk)
        serializer.save(author=contributor, issue=issue)


