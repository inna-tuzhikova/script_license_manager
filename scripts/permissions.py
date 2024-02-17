from rest_framework.permissions import BasePermission


class IsDeveloper(BasePermission):
    def has_permission(self, request, view):
        return True


class IsDemoUser(BasePermission):
    def has_permission(self, request, view):
        return True


class CanIssuePlain(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True


class CanIssueEncoded(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True
