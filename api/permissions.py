from rest_framework import permissions


class AdminOrSelfOnly(permissions.BasePermission):
    """
    Custom permission to allow a user to view their own profile
    """

    def has_object_permission(self, request, view, obj):
        return True  # request.user.is_superuser or request.user == obj


class UserHasProjectAccess(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.coreuser.is_member_of(obj)
