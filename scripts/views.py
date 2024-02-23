from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import ScriptFilter
from .models import IssuedLicense
from .models import Script as ScriptModel
from .permissions import (
    CanForceIssueEncodedScript,
    CanForceIssuePlainScript,
    CanIssueEncodedScript,
    CanIssuePlainScript,
    IsDownloadableScript,
)
from .serializers import (
    GenerateDemoEncodedRequestSerializer,
    GenerateEncodedRequestSerializer,
    GeneratePlainRequestSerializer,
    IssuedLicenseSerializer,
    ScriptSerializer,
    UpdateIssuedRequestSerializer,
)
from .services import lk_service, script_license_manager_service
from .services.script_license_manager_service.structures import (
    GeneratedScript,
    Script,
    ScriptLicenseConfig,
)

script_response = openapi.Response(
    'Script file to download',
    schema=openapi.Schema(type=openapi.TYPE_FILE),
)


@method_decorator(name='list', decorator=swagger_auto_schema(security=[]))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(security=[]))
class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """Set of views responsible for `script` resource

    Endpoints:
     - list of available scripts with pagination and filters (category, enabled,
       is_active, tag, without_tag)
     - script details
     - per script `generate_plain`
     - per script `generate_encoded`
     - per script `generate_demo_encoded`
     - per script `update_issued`
    """

    queryset = ScriptModel.objects.all()
    serializer_class = ScriptSerializer
    filterset_class = ScriptFilter
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method='post',
        operation_description='Generates non encoded script',
        request_body=GeneratePlainRequestSerializer,
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
            IsAuthenticated,
            IsDownloadableScript,
            CanForceIssuePlainScript | CanIssuePlainScript
        ],
    )
    def generate_plain(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GeneratePlainRequestSerializer(
            data=request.data, context=script
        )
        if serializer.is_valid():
            try:
                user_id = None if request.user is None else request.user.id
                generated = script_license_manager_service.generate_script(
                    script=Script(id=script.id),
                    config=ScriptLicenseConfig(
                        encode=False,
                        user_id=user_id,
                        **serializer.validated_data,
                    )
                )
            except PermissionError as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return self._prepare_python_file_response(generated)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_description='Generates encoded script',
        request_body=GenerateEncodedRequestSerializer,
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
            IsAuthenticated,
            IsDownloadableScript,
            CanForceIssueEncodedScript | CanIssueEncodedScript
        ],
    )
    def generate_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GenerateEncodedRequestSerializer(
            data=request.data, context=script
        )
        if serializer.is_valid():
            try:
                user_id = None if request.user is None else request.user.id
                generated = script_license_manager_service.generate_script(
                    script=Script(id=script.id),
                    config=ScriptLicenseConfig(
                        encode=True,
                        user_id=user_id,
                        **serializer.validated_data,
                    )
                )
            except PermissionError as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return self._prepare_python_file_response(generated)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_description='Generates encoded script for demo users',
        request_body=GenerateDemoEncodedRequestSerializer,
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
        permission_classes=[
            AllowAny,
            IsDownloadableScript,
            CanForceIssueEncodedScript | CanIssueEncodedScript
        ],
    )
    def generate_demo_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GenerateDemoEncodedRequestSerializer(
            data=request.data, context=script
        )
        if serializer.is_valid():
            demo = lk_service.is_demo_key(
                serializer.validated_data['license_key']
            )
            if not demo:
                return Response(
                    'Cannot issue license for not demo key',
                    status=status.HTTP_403_FORBIDDEN
                )
            try:
                user_id = None if request.user is None else request.user.id
                generated = script_license_manager_service.generate_script(
                    script=Script(id=script.id),
                    config=ScriptLicenseConfig(
                        encode=True,
                        user_id=user_id,
                        **serializer.validated_data,
                    )
                )
            except PermissionError as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return self._prepare_python_file_response(generated)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_description='Updates generated license',
        request_body=UpdateIssuedRequestSerializer,
        responses={
            status.HTTP_200_OK: script_response,
            status.HTTP_400_BAD_REQUEST: 'Invalid request params',
            status.HTTP_403_FORBIDDEN: (
                'Script has not been generated permanently for this key'
            ),
            status.HTTP_404_NOT_FOUND: 'Script not found',
        },
        produces='text/x-python',
        security=[],
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[
            AllowAny,
            IsDownloadableScript,
            CanForceIssueEncodedScript | CanIssueEncodedScript
        ],
    )
    def update_issued(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = UpdateIssuedRequestSerializer(
            data=request.data, context=script
        )
        if serializer.is_valid():
            try:
                user_id = None if request.user is None else request.user.id
                generated = script_license_manager_service.update_issued(
                    script=Script(id=script.id),
                    config=ScriptLicenseConfig(
                        encode=True,
                        user_id=user_id,
                        **serializer.validated_data
                    ))
            except PermissionError as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return self._prepare_python_file_response(generated)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def _prepare_python_file_response(
        self,
        generated: GeneratedScript
    ) -> Response:
        file_response = Response(
            headers={
                'Content-Disposition':
                    f'attachment; filename="{generated.filename}"',
                '1C-Filename':
                    generated.filename.replace(' ', '_').replace('.py', ''),
            },
            content_type='text/x-python',
        )
        file_response.content = generated.data
        return file_response


class IssuedLicensePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class IssuedLicenseViewSet(viewsets.ReadOnlyModelViewSet):
    """Set of views responsible for `issued_license` resource

    Endpoints:
     - issued licensed list with pagination
     - issued license details
    """

    queryset = IssuedLicense.objects.all()
    serializer_class = IssuedLicenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IssuedLicensePagination
