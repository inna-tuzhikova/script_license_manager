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
            'allow_issue_plain',
            'allow_issue_encoded', 'allow_issue_encoded_lk',
            'allow_issue_encoded_exp', 'allow_issue_encoded_lk_exp',
            'tags'
        ]


class IssuedLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedLicense
        fields = [
            'id', 'issued_at', 'license_key', 'script', 'issued_by',
            'issue_type', 'action', 'demo_lk', 'expires', 'extra_params',
        ]
