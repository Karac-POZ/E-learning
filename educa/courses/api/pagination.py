"""
Модуль для регистрации классов пагинации данных.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Класс для стандартизации параметров пагинации.

    Атрибуты:
        `page_size`: Количество элементов на странице (по умолчанию 10).
        `page_size_query_param`: Параметр запроса для изменения размера страницы.
        `max_page_size`: Максимальное количество элементов на странице (по умолчанию 50).
    """

    page_size = 10
    """Количество элементов на странице."""

    page_size_query_param = 'page_size'
    """
    Параметр запроса для изменения размера страницы.
    
    Например: `https://api.example.com/data/?page_size=20`
    """

    max_page_size = 50
    """Максимальное количество элементов на странице."""
