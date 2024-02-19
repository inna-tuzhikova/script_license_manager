from rest_framework.permissions import BasePermission

from .models import FORCE_ISSUE_PLAIN_SCRIPT, FORCE_ISSUE_ENCODED_SCRIPT


class CanForceIssuePlainScript(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_PLAIN_SCRIPT}')
        )


class CanForceIssueEncodedScript(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(f'scripts.{FORCE_ISSUE_ENCODED_SCRIPT}')
        )


class CanIssuePlainScript(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.allow_issue_plain


class CanIssueEncodedScript(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True


class IsDemoUser(BasePermission):
    def has_permission(self, request, view):
        return True
