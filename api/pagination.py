"""
Custom pagination for API endpoints
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with 20 results per page
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """
    Large pagination with 50 results per page
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Small pagination with 10 results per page
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
