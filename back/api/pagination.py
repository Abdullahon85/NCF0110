# api/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12                 # количество объектов на страницу по умолчанию
    page_size_query_param = 'page_size'  # позволяет клиенту указать ?page_size=20
    max_page_size = 100            # ограничение сверху


class LargeListPagination(PageNumberPagination):
    """For lists the frontend shows whole, without page switching (catalog tree,
    admin lists of brands, tags, messages, reviews...). Same response shape
    ({count, next, previous, results}); DRF's default would silently cut them at 12."""
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000
