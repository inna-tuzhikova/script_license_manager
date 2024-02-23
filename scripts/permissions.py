from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .models import FORCE_ISSUE_ENCODED_SCRIPT, FORCE_ISSUE_PLAIN_SCRIPT


class IsDownloadableScript(BasePermission):
    """Prevents from downloading disabled or deleted scripts"""

    message = 'Disabled or deleted script cannot be downloaded'

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.is_active and obj.enabled


class CanForceIssuePlainScript(BasePermission):
    """Checks user permission to download plain scripts despite specification

    Even if script specification forbids downloading plain version user with
    given permission can download it
    """

    message = 'No permissions to download plain script'

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_PLAIN_SCRIPT}')
        )


class CanForceIssueEncodedScript(BasePermission):
    """Checks user permission to download encoded scripts despite specification

    Even if script specification forbids downloading encoded version user with
    given permission can download it
    """

    message = 'No permissions to download encoded script'

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_ENCODED_SCRIPT}')
        )


class CanIssuePlainScript(BasePermission):
    """Checks if script specification allows to download plain script"""

    message = 'No permissions to download plain script'

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.allow_issue_plain


class CanIssueEncodedScript(BasePermission):
    """Checks if script specification allows to download encoded script"""

    message = 'No permissions to download encoded script'

    def has_object_permission(self, request: Request, view, obj) -> bool:
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
