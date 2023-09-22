from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class AuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        if request.method == "POST":
            return request.user.is_authenticated
        if request.method == "PATCH" or "DELETE":
            return obj.author == request.user
