from django.contrib import admin

# Импортирование модели сообщения из модуля chat.models
from chat.models import Message


# Регистрация административного интерфейса для модели сообщения
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Класс для настройки административного интерфейса модели сообщения.

    Attributes:
        list_display (list): Поля, которые будут отображаться в списке сообщений.
        list_filter (list): Поля, по которым можно фильтровать список сообщений.
        search_fields (list): Поля, по которым можно произвести поиск сообщений.
        raw_id_fields (list): Поля, которые отображаются в виде ID-номера в списке сообщений.
    """

    # Отображение полей в списке сообщений
    list_display = ['sent_on', 'user', 'course', 'content']

    # Фильтрация по полям в списке сообщений
    list_filter = ['sent_on', 'course']

    # Поиск по содержимому сообщения
    search_fields = ['content']

    # Отображение ID-номера пользователей и курсов в списке сообщений
    raw_id_fields = ['user', 'course']
