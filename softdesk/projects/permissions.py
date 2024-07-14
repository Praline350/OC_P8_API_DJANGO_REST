from rest_framework.permissions import BasePermission

from projects.models import Contributor, Project, Issue, Comment


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            is_author = obj.author == request.user
            # print(f"Debug: IsAuthor (Project) - User: {request.user.username}, Object Author: {obj.author.username}, Is Author: {is_author}")
        else:  # obj is Issue or Comment
            is_author = obj.author.user == request.user
            # print(f"Debug: IsAuthor (Issue/Comment) - User: {request.user.username}, Object Author: {obj.author.user.username}, Is Author: {is_author}")
        return is_author


class IsProjectContributor(BasePermission):
    """
    Permission class to check if the user is a contributor to the project.
    """

    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk') or view.kwargs.get('pk')
        is_contributor = Contributor.objects.filter(project_id=project_pk, user=request.user).exists()
        # print(f"Debug: IsProjectContributor - User: {request.user.username}, Project: {project_pk}, Is Contributor: {is_contributor}")
        return is_contributor
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            is_contributor = Contributor.objects.filter(project=obj, user=request.user).exists()
            # print(f"Debug: IsProjectContributor (Project) - User: {request.user.username}, Project: {obj.id}, Is Contributor: {is_contributor}")
            return is_contributor
        elif isinstance(obj, Issue):
            is_contributor = Contributor.objects.filter(project=obj.project, user=request.user).exists()
            # print(f"Debug: IsProjectContributor (Issue) - User: {request.user.username}, Project: {obj.project.id}, Is Contributor: {is_contributor}")
            return is_contributor
        elif isinstance(obj, Comment):
            is_contributor = Contributor.objects.filter(project=obj.issue.project, user=request.user).exists()
            # print(f"Debug: IsProjectContributor (Comment) - User: {request.user.username}, Project: {obj.issue.project.id}, Is Contributor: {is_contributor}")
            return is_contributor
        return False
