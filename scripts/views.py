from datetime import date, timedelta

import jsonschema
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone

from .filters import ScriptFilter
from .models import Script, IssuedLicense
from .permissions import (
    IsDownloadable,
    CanForceIssuePlainScript,
    CanForceIssueEncodedScript,
    CanIssuePlainScript,
    CanIssueEncodedScript,
)
from .serializers import (
    GeneratePlainRequestSerializer,
    GenerateEncodedRequestSerializer,
    GenerateDemoEncodedRequestSerializer,
    UpdateIssuedRequestSerializer,
    ScriptSerializer,
    IssuedLicenseSerializer, RequestWithExpirationSerializer
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
            IsDownloadable,
            CanForceIssuePlainScript | CanIssuePlainScript
        ],
    )
    def generate_plain(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GeneratePlainRequestSerializer(data=request.data)
        if serializer.is_valid():
            mb_response = self._validate_extra_params(serializer, script)
            if mb_response is not None:
                return mb_response
            self._make_issue_record(
                serializer,
                script=script,
                issued_by=request.user,
                issue_type=IssuedLicense.IssueType.PLAIN,
                action_str=IssuedLicense.Action.GENERATE,
                demo_lk=False,
            )
            return Response(dict(hello=script.name))
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
            IsDownloadable,
            CanForceIssueEncodedScript | CanIssueEncodedScript
        ]
    )
    def generate_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GenerateEncodedRequestSerializer(data=request.data)
        if serializer.is_valid():
            maybe_response = self._validate_extra_params(serializer, script)
            if maybe_response is not None:
                return maybe_response
            is_demo = False
            license_key = serializer.validated_data.get('license_key')
            if license_key is not None:
                is_demo = is_demo_key(license_key)
                maybe_response = self._validate_expiration(serializer, is_demo)
                if maybe_response is not None:
                    return maybe_response
            self._make_issue_record(
                serializer,
                script=script,
                issued_by=request.user,
                issue_type=self._get_issue_type(serializer),
                action_str=IssuedLicense.Action.GENERATE,
                demo_lk=is_demo,
            )
            return Response(dict(hello=script.name))
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
        permission_classes=[AllowAny, IsDownloadable]
    )
    def generate_demo_encoded(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = GenerateDemoEncodedRequestSerializer(data=request.data)
        if serializer.is_valid():
            is_demo = is_demo_key(serializer.validated_data['license_key'])
            if not is_demo:
                return Response(
                    'Cannot issue license for not demo key',
                    status=status.HTTP_403_FORBIDDEN
                )
            maybe_response = self._validate_expiration(serializer, True)
            if maybe_response is not None:
                return maybe_response
            self._make_issue_record(
                serializer,
                script=script,
                issued_by=request.user,
                issue_type=self._get_issue_type(serializer),
                action_str=IssuedLicense.Action.GENERATE,
                demo_lk=True,
            )
            return Response(dict(hello=script.name))
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
        permission_classes=[AllowAny, IsDownloadable]
    )
    def update_issued(self, request: Request, *args, **kwargs):
        script = self.get_object()
        serializer = UpdateIssuedRequestSerializer(data=request.data)
        if serializer.is_valid():
            license_key = serializer.validated_data['license_key']
            issued = IssuedLicense.object.filter(
                script=script,
                license_key=license_key
            ).first()
            if issued is None or not issued.is_permanent():
                return Response(
                    'Script has not been generated permanently for this key',
                    status=status.HTTP_403_FORBIDDEN
                )
            is_demo = is_demo_key(license_key)
            maybe_response = self._validate_expiration(serializer, is_demo)
            if maybe_response is not None:
                return maybe_response
            self._make_issue_record(
                serializer,
                script=script,
                issued_by=request.user,
                issue_type=self._get_issue_type(serializer),
                action_str=IssuedLicense.Action.UPDATE,
                demo_lk=is_demo,
            )
            return Response(dict(hello=script.name))
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def _validate_extra_params(self, serializer, script) -> None | Response:
        schema = script.extra_params_schema
        if schema is not None:
            extra_params = serializer.validated_data.get('extra_params')
            if extra_params is None:
                return Response(
                    f'`extra_params` is required for {script.name}. '
                    f'Check schema: {schema}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                jsonschema.validate(instance=extra_params, schema=schema)
            except jsonschema.exceptions.ValidationError:
                return Response(
                    f'Invalid `extra_params` for {script.name}. '
                    f'Check schema: {schema}',
                    status=status.HTTP_400_BAD_REQUEST
                )

    def _validate_expiration(
        self,
        serializer: RequestWithExpirationSerializer,
        is_demo: bool
    ) -> None | Response:
        today = date.today()
        expires_key = 'expires'
        data = serializer.validated_data
        expires = data.get(expires_key)
        if is_demo:
            if expires is None:
                data[expires_key] = today + timedelta(
                    days=settings.DEMO_KEY_DEFAULT_EXPIRATION_DAYS
                )
            else:
                max_date = today + timedelta(
                    days=settings.DEMO_KEY_MAX_EXPIRATION_DAYS
                )
                if expires > max_date:
                    data[expires_key] = max_date
        else:
            if expires is not None:
                max_date = today + timedelta(
                    days=settings.USER_KEY_MAX_EXPIRATION_DAYS
                )
                if expires > max_date:
                    return Response(
                        f'Trial for non demo key cannot exceed '
                        f'{settings.USER_KEY_MAX_EXPIRATION_DAYS} days',
                        status=status.HTTP_403_FORBIDDEN
                    )

    def _get_issue_type(self, serializer) -> IssuedLicense.IssueType | None:
        result = None
        got_license_key = serializer.validated_data.get(
            'license_key'
        ) is not None
        got_expires = serializer.validated_data.get(
            'expires'
        ) is not None

        if got_license_key and got_expires:
            result = IssuedLicense.IssueType.ENCODED_EXP_LK
        elif not got_license_key and got_expires:
            result = IssuedLicense.IssueType.ENCODED_EXP
        elif got_license_key and not got_expires:
            result = IssuedLicense.IssueType.ENCODED_LK
        elif not got_license_key and not got_expires:
            result = IssuedLicense.IssueType.ENCODED
        return result

    def _make_issue_record(
        self,
        serializer,
        script: Script,
        issued_by: None | User,
        issue_type: str,
        action_str: str,
        demo_lk: bool,
    ):
        IssuedLicense.objects.create(
            issued_at=timezone.now(),
            license_key=serializer.validated_data.get('license_key'),
            script=script,
            issued_by=issued_by,
            issue_type=issue_type,
            action=action_str,
            demo_lk=demo_lk,
            expires=serializer.validated_data.get('expires'),
            extra_params=serializer.validated_data.get('extra_params'),
        )


def is_demo_key(lk: str) -> bool:
    return False


class IssuedLicensePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class IssuedLicenseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IssuedLicense.objects.all()
    serializer_class = IssuedLicenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = IssuedLicensePagination
