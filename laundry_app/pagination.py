from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from urllib.parse import urlparse, parse_qs


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_number_from_url(self, url):
        if not url:
            return None
        query_params = parse_qs(urlparse(url).query)
        return int(query_params.get('page', [None])[0])

    def get_paginated_response(self, data):
        next_page = self.get_page_number_from_url(self.get_next_link())
        previous_page = self.get_page_number_from_url(self.get_previous_link())

        return Response({
            'count': self.page.paginator.count,
            'next': next_page,
            'previous': previous_page,
            'results': data
        })
