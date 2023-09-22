from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    limit = 5
    page_size_query_param = "limit"
    max_page_size = 1000
