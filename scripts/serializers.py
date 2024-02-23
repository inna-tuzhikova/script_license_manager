import re
from datetime import date

import jsonschema
from rest_framework import serializers

from .models import IssuedLicense, Script, Tag


class LicenseKeyField(serializers.CharField):
    _USB_KEY_PATTERN = re.compile(r'^0x[0-9a-fA-F]{8}$')
    _SRL_KEY_PATTERN = re.compile(
        r'^[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}$'
    )

    def __init__(self, **kwargs):
        kwargs.update(allow_blank=False, trim_whitespace=True)
        super().__init__(**kwargs)
        self.validators.append(self.license_key_validator)

    def license_key_validator(self, value):
        if len(value) == 8:
            value = f'0x{value}'
        elif len(value) == 10:
            value = f'0x{value[2:]}'
        if not (
            self._USB_KEY_PATTERN.match(value)
            or self._SRL_KEY_PATTERN.match(value)
        ):
            raise serializers.ValidationError(
                f'Unexpected license key. '
                f'Expected `0x00000000` or `0000-0000-0000-0000`. '
                f'Got `{value}`.'
            )
        return value


class RequestWithExpirationSerializer(serializers.Serializer):
    expires = serializers.DateField(required=False, allow_null=True)

    def validate_expires(self, value):
        if value is not None:
            if value <= date.today():
                raise serializers.ValidationError(
                    'Expiration date should be set later than today'
                )
        return value


class RequestWithExtraParamsSerializer(serializers.Serializer):
    extra_params = serializers.JSONField(
        binary=True, required=False, allow_null=True
    )

    def validate(self, attrs):
        if not isinstance(self.context, Script):
            raise RuntimeError(
                'Pass script ctx to validate extra_params'
            )
        schema = self.context.extra_params_schema
        if schema is not None:
            extra_params = attrs.get('extra_params')
            if extra_params is None:
                raise serializers.ValidationError(
                    f'`extra_params` is required for {self.context.name}. '
                    f'Check schema: {schema}',
                )
            try:
                jsonschema.validate(instance=extra_params, schema=schema)
            except jsonschema.exceptions.ValidationError:
                raise serializers.ValidationError(
                    f'Invalid `extra_params` for {self.context.name}. '
                    f'Check schema: {schema}'
                )
        return attrs


class GeneratePlainRequestSerializer(RequestWithExtraParamsSerializer):
    pass


class GenerateEncodedRequestSerializer(
    RequestWithExpirationSerializer,
    RequestWithExtraParamsSerializer,
):
    license_key = LicenseKeyField(required=False, allow_null=True)


class GenerateDemoEncodedRequestSerializer(
    RequestWithExpirationSerializer,
    RequestWithExtraParamsSerializer
):
    license_key = LicenseKeyField(required=True, allow_null=False)


class UpdateIssuedRequestSerializer(GenerateDemoEncodedRequestSerializer):
    pass


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ScriptSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Script
        fields = [
            'id', 'name', 'description', 'category', 'enabled', 'is_active',
            'extra_params_schema',
            'allow_issue_plain',
            'allow_issue_encoded', 'allow_issue_encoded_lk',
            'allow_issue_encoded_exp', 'allow_issue_encoded_lk_exp',
            'tags'
        ]


class IssuedLicenseSerializer(serializers.ModelSerializer):
    issued_by = serializers.ReadOnlyField(source='issued_by.username')

    class Meta:
        model = IssuedLicense
        fields = [
            'id', 'issued_at', 'license_key', 'script', 'issued_by',
            'issue_type', 'action', 'demo_lk', 'expires', 'extra_params',
        ]
