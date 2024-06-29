"""
URL configuration for softdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from django.urls import path, include

from authentication.views import UserViewset
from projects.views import ProjectViewset, ContributoViewset

router = routers.SimpleRouter()

router.register(r'user', UserViewset, basename='user')
router.register(r'project', ProjectViewset, basename='project')
router.register(r'contributor', ContributoViewset, basename='contributor')

urlpatterns = [

    # API & Admin
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),

    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    

]
