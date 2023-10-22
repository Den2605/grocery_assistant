from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class AuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Разрешение для автора или безопасных методов.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверка, является ли пользователь автором объекта.
        """
        return request.method in SAFE_METHODS or obj.author == request.user
