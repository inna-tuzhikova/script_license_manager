from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ScriptViewSet, IssuedLicenseViewSet


router = DefaultRouter()
router.register('scripts', ScriptViewSet, basename='script')
router.register(
    'issued_licenses', IssuedLicenseViewSet, basename='issued_license'
)

urlpatterns = [
    path('', include(router.urls)),
]
