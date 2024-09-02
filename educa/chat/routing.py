"""
Регистрация вебсокетных URL-шаблонов для чата.

Ниже приведены URL-шаблоны для подключения к вебсокету в чате.
"""

from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    """
    URL-шаблон для подключения к вебсокету в чате.

    Параметр `course_id` — идентификатор курса.
    """
    re_path(
        r'ws/chat/room/(?P<course_id>\d+)/$',
        consumers.ChatConsumer.as_asgi(),
    ),
]
