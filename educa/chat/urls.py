"""
Модуль для регистрации URL-шаблонов приложения «Чат».

В этом модуле содержится функция `urlpatterns` для определения URL-шаблонов
чата.
"""

from django.urls import path  # noqa: F401 (используется только один раз)

from . import views


app_name = 'chat'  # Имя приложения «Чат»

urlpatterns = [
    """
    URL-шаблон для доступа к странице чата в конкретном курсе.

    Параметр `course_id` — идентификатор курса.
    
    URL: /room/<int:course_id>/
    """
    path(
        'room/<int:course_id>/',
        views.course_chat_room,
        name='course_chat_room',  # Имя URL-шаблона
    ),
]
