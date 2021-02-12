from rest_framework import permissions


class UserHasProjectAccess(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.coreuser.member_of(obj)
