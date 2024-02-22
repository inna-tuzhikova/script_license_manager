from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .models import FORCE_ISSUE_PLAIN_SCRIPT, FORCE_ISSUE_ENCODED_SCRIPT


class IsDownloadableScript(BasePermission):
    message = 'Disabled or deleted script cannot be downloaded'

    def has_object_permission(self, request, view, obj):
        return obj.is_active and obj.enabled


class CanForceIssuePlainScript(BasePermission):
    message = 'No permissions to download plain script'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_PLAIN_SCRIPT}')
        )


class CanForceIssueEncodedScript(BasePermission):
    message = 'No permissions to download encoded script'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_ENCODED_SCRIPT}')
        )


class CanIssuePlainScript(BasePermission):
    message = 'No permissions to download plain script'

    def has_object_permission(self, request, view, obj):
        return obj.allow_issue_plain


class CanIssueEncodedScript(BasePermission):
    message = 'No permissions to download encoded script'

    def has_object_permission(self, request: Request, view, obj):
        got_license_key = request.data.get('license_key') is not None
        got_expires = request.data.get('expires') is not None

        if not got_license_key and not got_expires:
            result = obj.allow_issue_encoded
        elif got_license_key and not got_expires:
            result = obj.allow_issue_encoded_lk
        elif not got_license_key and got_expires:
            result = obj.allow_issue_encoded_exp
        else:
            result = obj.allow_issue_encoded_lk_exp
        return result
