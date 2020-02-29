from rest_framework import permissions

from api.models.user import Role


class IsAdministrator(permissions.BasePermission):
    """
    Check if the current user has role: Administrator
    """

    def has_permission(self, request, view):
        # Any user can perform GET, HEAD and OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only ADMINISTRATOR can create, update and delete
        return request.user.role == Role.ADMINISTRATOR.name

    def has_object_permission(self, request, view, obj):
        # Any user can perform GET, HEAD and OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role == Role.ADMINISTRATOR.name
