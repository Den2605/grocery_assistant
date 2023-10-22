from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Класс для кастомной пагинации."""

    limit = 6
    page_size_query_param = "limit"
    max_page_size = 1000
