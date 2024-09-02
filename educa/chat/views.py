"""
Модуль для регистрации функций представления приложения «Чат».

В этом модуле содержится функция `course_chat_room` для доступа к странице чата в конкретном курсе.
"""

from django.contrib.auth.decorators import login_required  # noqa: F401 (используется только один раз)
from django.http import HttpResponseForbidden
from django.shortcuts import render

from courses.models import Course  # noqa: F401 (используется только один раз)


@login_required
def course_chat_room(request, course_id):
    """
    Функция для доступа к странице чата в конкретном курсе.

    Параметры:
        `request`: Объект запроса.
        `course_id`: Идентификатор курса.

    Возвращает HTML-страницу с последними сообщениями в чате.
    """
    try:
        # Получение курса по идентификатору
        course = request.user.courses_joined.get(id=course_id)
    except Course.DoesNotExist:
        # Возврат запрещенного доступа, если курс не существует
        return HttpResponseForbidden()

    # Получение последних 5 сообщений в чате
    latest_messages = course.chat_messages.select_related(
        'user'
    ).order_by('-id')[:5]
    # Отображение последних сообщений
    latest_messages = reversed(latest_messages)

    # Возврат HTML-страницы с последними сообщениями
    return render(
        request,
        'chat/room.html',
        {'course': course, 'latest_messages': latest_messages},
    )
