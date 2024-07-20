from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from projects.permissions import IsOwner
from authentication.serializers import UserListSerializer, UserDetailSerializer

User = get_user_model()


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class UserViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = UserListSerializer
    detail_serializer_class = UserDetailSerializer
    
    def get_queryset(self):
        return User.objects.all()
    
    def get_permissions(self):
        match self.action:
            case 'create':
                self.permission_classes = [AllowAny]
            case 'update' |'partial_update' | 'destroy':
                self.permission_classes = [IsAuthenticated, IsOwner]
            case _:
                self.permission_classes = [IsAuthenticated]
        return super().get_permissions()