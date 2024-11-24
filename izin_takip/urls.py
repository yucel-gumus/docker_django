from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views 
schema_view = get_schema_view(
   openapi.Info(
      title="İzin Takip API",
      default_version='v1',
      description="API dokümantasyonu",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django admin paneli için URL
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    # Accounts uygulamasının URL'leri
    path('accounts/', include('accounts.urls')),

    # Leave Management uygulamasının URL'leri
    path('leave/', include('leave_management.urls')),

    # Swagger dokümantasyonu için URL
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
