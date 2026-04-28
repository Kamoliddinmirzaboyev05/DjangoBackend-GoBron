from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only to users with user_role='OWNER'."""

    message = 'Access restricted to owner users only.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_role == 'OWNER'
        )
