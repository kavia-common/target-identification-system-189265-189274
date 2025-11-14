"""
Pagination classes for the API.

This module isolates pagination definitions to avoid circular import issues
when Django REST Framework loads settings and attempts to import the default
pagination class.
"""
from rest_framework.pagination import PageNumberPagination


# PUBLIC_INTERFACE
class DefaultPagination(PageNumberPagination):
    """Default pagination for the API."""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200
