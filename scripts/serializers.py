from rest_framework import serializers

from .models import Script, Tag, IssuedLicense


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
            'allow_issue_plain', 'allow_issue_wo_lk',
            'allow_issue_w_lk', 'allow_issue_w_expiration',
            'tags'
        ]


class IssuedLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedLicense
        fields = [
            'id', 'issued_at', 'license_key', 'script', 'issued_by',
            'demo_lk', 'expires', 'extra_params', 'action'
        ]
