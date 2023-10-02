from rest_framework import permissions


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
        if request.method == "PATCH":
            return obj.author == request.user
        if request.method == "DELETE":
            return obj.author == request.user
