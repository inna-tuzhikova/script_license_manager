from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination

from .filters import ScriptFilter
from .models import Script, IssuedLicense
from .permissions import (
    CanForceIssuePlainScript,
    CanForceIssueEncodedScript,
    CanIssuePlainScript,
    CanIssueEncodedScript,
    IsDemoUser
)
from .serializers import ScriptSerializer, IssuedLicenseSerializer


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    filterset_class = ScriptFilter
    permission_classes = [AllowAny]

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated & (
                CanForceIssuePlainScript | CanIssuePlainScript
            )
        ]
    )
    def generate_plain(self, request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated & (
                CanForceIssueEncodedScript | CanIssueEncodedScript
            )
        ]
    )
    def generate_encoded(self, request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[AllowAny, IsDemoUser]
    )
    def generate_demo_encoded(self, request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[AllowAny]
    )
    def update_encoded(self, request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))


class IssuedLicensePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class IssuedLicenseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IssuedLicense.objects.all()
    serializer_class = IssuedLicenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IssuedLicensePagination
