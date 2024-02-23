from django.contrib.auth.models import Permission, User
from django.utils import timezone

from scripts.models import IssuedLicense, Script


def get_default_user():
    user = User.objects.create_user(
        username='test_user',
        email='test@example.com',
        password='test_password'
    )
    return user


def give_permission_to_user(user: User, permission_codename: str):
    perm = Permission.objects.get(codename=permission_codename)
    user.user_permissions.add(perm)


def update_user(user: User, **fields) -> None:
    User.objects.filter(pk=user.pk).update(**fields)


def get_default_script(**fields):
    default_fields = dict(
        id='test_script',
        name='Test Script',
        description='Script for testing purposes',
        category_id='free_scripts',
        enabled=True,
        is_active=True,
        extra_params_schema=None,
        allow_issue_plain=True,
        allow_issue_encoded=True,
        allow_issue_encoded_lk=True,
        allow_issue_encoded_exp=True,
        allow_issue_encoded_lk_exp=True,
    )
    default_fields.update(fields)
    return Script.objects.create(**default_fields)


def update_script(script: Script, **fields) -> None:
    Script.objects.filter(pk=script.pk).update(**fields)


def get_default_issued(script: Script, user: User, **fields) -> IssuedLicense:
    default_fields = dict(
        issued_at=timezone.now(),
        license_key='0x12345678',
        script=script,
        issued_by=user,
        issue_type='ENCODED_LK',
        action='GENERATE',
        demo_lk=True,
        expires=None,
        extra_params=None
    )
    default_fields.update(fields)
    return IssuedLicense.objects.create(**default_fields)


def update_issued(issued: IssuedLicense, **fields) -> None:
    IssuedLicense.objects.filter(pk=issued.pk).update(**fields)


default_json_schema = dict(
    type='object',
    required=['a', 'b'],
    properties=dict(
        a=dict(type='integer', minimum=1, maximum=10),
        b=dict(type='string', enum=['b1', 'b2', 'b3'])
    )
)
