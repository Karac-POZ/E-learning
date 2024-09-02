"""
Модуль для вкатки студента в курс.
"""

from rest_framework.permissions import BasePermission


class IsEnrolled(BasePermission):
    """
    Класс для проверки причастности пользователя к курсу.

    Атрибуты:
        `request`: Объект запроса.
        `view`: Объект представления.
        `obj`: Объект данных (курс).

    Методы:
        `has_object_permission`: Функция проверки разрешения доступа.
    """

    def has_object_permission(self, request, view, obj):
        """
        Функция проверки разрешения доступа.

        Проверяет, причастен ли пользователь к курсу. Если да, возвращает True; иначе False.

        Аргументы:
            `request`: Объект запроса.
            `view`: Объект представления.
            `obj`: Объект данных (курс).

        Возвращает:
            `True` - пользователь причастен к курсу;
            `False` - пользователь не причастен к курсу.
        """

        # Проверка причастности пользователя к курсу
        return obj.students.filter(id=request.user.id).exists()
