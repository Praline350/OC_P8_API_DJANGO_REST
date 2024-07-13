from rest_framework.permissions import BasePermission

from projects.models import Contributor


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsProjectContributor(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('pk') or view.kwargs.get('project_pk')
        if project_id is None:
            return True  # Permettre l'accès pour les actions qui ne nécessitent pas de projet spécifique
        return Contributor.objects.filter(project_id=project_id, user=request.user).exists()
    
    def has_object_permission(self, request, view, obj):
        return Contributor.objects.filter(project=obj, user=request.user).exists()