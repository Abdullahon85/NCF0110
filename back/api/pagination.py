# api/pagination.py
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12  # количество объектов на страницу по умолчанию
    page_size_query_param = "page_size"  # позволяет клиенту указать ?page_size=20
    max_page_size = 100  # ограничение сверху


class LargeListPagination(PageNumberPagination):
    """For lists the frontend shows whole, without page switching (catalog tree,
    admin lists of brands, messages, reviews...). Same response shape
    ({count, next, previous, results}); DRF's default would silently cut them at 12."""

    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 1000


class CatalogPagination(PageNumberPagination):
    """Product lists of the site: 20 / 40 / 80 per page (anything else -> 20); a page past
    the end gives the last page instead of a 404, so an old link never shows an error."""

    def paginate_queryset(self, queryset, request, view=None):
        from .catalog import page_size

        self.request = request
        paginator = self.django_paginator_class(queryset, page_size(request.query_params))
        try:
            number = int(request.query_params.get(self.page_query_param, 1))
        except (TypeError, ValueError):
            number = 1
        self.page = paginator.page(max(1, min(number, paginator.num_pages)))
        return list(self.page)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["page"] = self.page.number
        response.data["page_size"] = self.page.paginator.per_page
        return response
