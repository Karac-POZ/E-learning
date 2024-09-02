# Импортируем необходимые библиотеки и модели из других файлов.
# Для подсчета количества курсов по предмету.
from django.db.models import Count
from rest_framework import viewsets  # Для создания API-виджетов.
# Для авторизации пользователя.
from rest_framework.authentication import BasicAuthentication
# Для добавления действий к API-виджету.
from rest_framework.decorators import action
# Для проверки авторизации пользователя.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response  # Для возвращения ответа клиенту.

# Импортируем настройки пагинации и разрешения для API-виджетов.
from courses.api.pagination import StandardPagination
from courses.api.permissions import IsEnrolled

# Импортируем сериализаторы данных для предметов и курсов.
from courses.api.serializers import (
    CourseSerializer,  # Для сериализации данных по курсу.
    # Для сериализации данных по курсу с содержимым.
    CourseWithContentsSerializer,
    SubjectSerializer,  # Для сериализации данных по предмету.
)

# Импортируем модели предметов и курсов из других файлов.
from courses.models import Course, Subject


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API-виджет для работы с предметами.

    Поля:
        queryset (QuerySet): Коллекция объектов по умолчанию.
        serializer_class (Serializer): Класс сериализации данных.
        pagination_class (Pagination): Класс пагинации данных.
    """

    # Установка коллекции объектов по умолчанию с подсчетом количества курсов по предмету.
    queryset = Subject.objects.annotate(total_courses=Count('courses'))

    # Установка класса сериализации данных для предмета.
    serializer_class = SubjectSerializer

    # Установка класса пагинации данных.
    pagination_class = StandardPagination


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API-виджет для работы с курсами.

    Поля:
        queryset (QuerySet): Коллекция объектов по умолчанию.
        serializer_class (Serializer): Класс сериализации данных.
        pagination_class (Pagination): Класс пагинации данных.
    """

    # Установка коллекции объектов по умолчанию с предварительной загрузкой модулей для каждого курса.
    queryset = Course.objects.prefetch_related('modules')

    # Установка класса сериализации данных для курса.
    serializer_class = CourseSerializer

    # Установка класса пагинации данных.
    pagination_class = StandardPagination

    @action(
        detail=True,
        methods=['post'],
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated],
    )
    # Действие для регистрации пользователя в курсе.
    # Поля:
    # request (Request): Объект запроса.
    # *args: Аргументы.
    # **kwargs: Ключевые аргументы.
    # Возвращаемые данные:
    # Response: Ответ клиенту.
    def enroll(self, request, *args, **kwargs):
        # Получение текущего курса.
        course = self.get_object()

        # Добавление пользователя в список студентов для данного курса.
        course.students.add(request.user)

        # Возвращение ответа клиенту с информацией о регистрации.
        return Response({'enrolled': True})

    @action(
        detail=True,
        methods=['get'],
        serializer_class=CourseWithContentsSerializer,
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated, IsEnrolled],
    )
    # Действие для получения содержимого курса.
   # Поля:
    # request (Request): Объект запроса.
    # *args: Аргументы.
    # **kwargs: Ключевые аргументы.
    # Возвращаемые данные:
    # Response: Ответ клиенту.
    def contents(self, request, *args, **kwargs):
        # Возвращение содержимого курса в виде ответа клиенту.
        return self.retrieve(request, *args, **kwargs)
