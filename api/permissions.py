from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AdminOrSelfOnly(permissions.BasePermission):
    """
    Custom permission to allow a user to view their own profile
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj


class UserHasProjectMemberAccess(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.has_member_access(obj)


class UserHasProjectAccess(permissions.BasePermission):
    """
    Custom permission to only allow subscribers read access, or the ability to lock & sync if they have access.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            (request.method in SAFE_METHODS or view.action == 'lock') and
            request.user.has_subscriber_access(obj) or
            request.user.has_member_access(obj)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a read-only request by an authenticated user.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_superuser
        )


class CreateOrReadOnly(permissions.BasePermission):
    """
    User should be able to create a record, but not update or delete it unless superuser.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in ('GET', 'POST') or request.user.is_superuser
        )
