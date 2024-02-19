from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from django.utils.decorators import method_decorator

from .filters import ScriptFilter
from .models import Script, IssuedLicense
from .permissions import (
    CanForceIssuePlainScript,
    CanForceIssueEncodedScript,
    CanIssuePlainScript,
    CanIssueEncodedScript,
    IsDemoUser
)
from .serializers import (
    DownloadScriptRequestSerializer,
    ScriptSerializer,
    IssuedLicenseSerializer
)


script_response = openapi.Response(
    'Script file to download',
    schema=openapi.Schema(type=openapi.TYPE_FILE),
)


@method_decorator(name='list', decorator=swagger_auto_schema(security=[]))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(security=[]))
class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    filterset_class = ScriptFilter
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method='post',
        operation_description='Generates non encoded script',
        request_body=DownloadScriptRequestSerializer,
        responses={
            status.HTTP_200_OK: script_response,
            status.HTTP_400_BAD_REQUEST: 'Invalid request params',
            status.HTTP_401_UNAUTHORIZED: 'No credentials provided',
            status.HTTP_403_FORBIDDEN: 'Not authorised',
            status.HTTP_404_NOT_FOUND: 'Script not found'
        },
        produces='text/x-python',
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated & (
                CanForceIssuePlainScript | CanIssuePlainScript
            )
        ],
    )
    def generate_plain(self, request: Request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @swagger_auto_schema(
        method='post',
        operation_description='Generates encoded script',
        request_body=DownloadScriptRequestSerializer,
        responses={
            status.HTTP_200_OK: script_response,
            status.HTTP_400_BAD_REQUEST: 'Invalid request params',
            status.HTTP_401_UNAUTHORIZED: 'No credentials provided',
            status.HTTP_403_FORBIDDEN: 'Not authorised',
            status.HTTP_404_NOT_FOUND: 'Script not found'
        },
        produces='text/x-python',
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            IsAuthenticated & (
                CanForceIssueEncodedScript | CanIssueEncodedScript
            )
        ]
    )
    def generate_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @swagger_auto_schema(
        method='post',
        operation_description='Generates encoded script for demo users',
        request_body=DownloadScriptRequestSerializer,
        responses={
            status.HTTP_200_OK: script_response,
            status.HTTP_400_BAD_REQUEST: 'Invalid request params',
            status.HTTP_403_FORBIDDEN: 'Cannot issue license for not demo key',
            status.HTTP_404_NOT_FOUND: 'Script not found'
        },
        produces='text/x-python',
        security=[]
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[AllowAny, IsDemoUser]
    )
    def generate_demo_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        return Response(dict(hello=script.name))

    @swagger_auto_schema(
        method='post',
        operation_description='Updates generated license',
        request_body=DownloadScriptRequestSerializer,
        responses={
            status.HTTP_200_OK: script_response,
            status.HTTP_400_BAD_REQUEST: 'Invalid request params',
            status.HTTP_403_FORBIDDEN: 'Cannot update temporary license',
            status.HTTP_404_NOT_FOUND: 'Script not found',
        },
        produces='text/x-python',
        security=[],
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[AllowAny]
    )
    def update_encoded(self, request: Request, *args, **kwargs):
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
