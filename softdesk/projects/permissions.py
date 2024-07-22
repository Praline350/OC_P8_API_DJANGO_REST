from rest_framework.permissions import BasePermission

from projects.models import Contributor, Project, Issue, Comment



class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = obj == request.user
        return is_owner

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            is_author = obj.author == request.user
        else:  # obj is Issue or Comment
            is_author = obj.author.user == request.user
        return is_author


class IsProjectContributor(BasePermission):
    """
    Permission class to check if the user is a contributor to the project.
    """

    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk') or view.kwargs.get('pk')
        is_contributor = Contributor.objects.filter(project_id=project_pk, user=request.user).exists()
        return is_contributor
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            is_contributor = Contributor.objects.filter(project=obj, user=request.user).exists()
            return is_contributor
        elif isinstance(obj, Issue):
            is_contributor = Contributor.objects.filter(project=obj.project, user=request.user).exists()
            return is_contributor
        elif isinstance(obj, Comment):
            is_contributor = Contributor.objects.filter(project=obj.issue.project, user=request.user).exists()
            return is_contributor
        return False
