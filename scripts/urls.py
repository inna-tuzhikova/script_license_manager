from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import ScriptViewSet, IssuedLicenseViewSet


schema_view = get_schema_view(
    openapi.Info(
        title='Script License Manager API',
        default_version='v1',
    ),
    public=True,
    permission_classes=[AllowAny],
)


router = DefaultRouter()
router.register('scripts', ScriptViewSet, basename='script')
router.register(
    'issued_licenses', IssuedLicenseViewSet, basename='issued_license'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
]
