from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "me":
            if request.user.is_authenticated:
                return True
            else:
                return False
        return True
