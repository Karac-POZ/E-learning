# Импортируем необходимые библиотеки для администрирования.
from django.contrib import admin  # Для работы с админ-панелями.

# Импортируем модели предметов, курсов и модулей из других файлов.
from .models import Course, Module, Subject


# Регистрация админ-виджета для предмета с настройками по умолчанию.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Админ-виджет для предмета.

    Поля:
        list_display (list): Список полей для отображения в таблице.
        prepopulated_fields (dict): Словарь полей с предустановленными значениями.
    """

    # Настройка списка полей для отображения в таблице.
    list_display = ['title', 'slug']

    # Настройка полей с предустановленными значениями.
    prepopulated_fields = {'slug': ('title',)}


# Класс для настройки отображения модулей в админ-панели.
class ModuleInline(admin.StackedInline):
    """
    Класс для настройки отображения модулей.

    Поля:
        model (Model): Модель для работы с данными.
    """

    # Настройка модели для работы с данными.
    model = Module


# Регистрация админ-виджета для курса с настройками по умолчанию.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Админ-виджет для курса.

    Поля:
        list_display (list): Список полей для отображения в таблице.
        list_filter (list): Список полей для фильтрации данных.
        search_fields (list): Список полей для поиска данных.
        prepopulated_fields (dict): Словарь полей с предустановленными значениями.
        inlines (list): Список инлайновых админ-виджетов.
    """

    # Настройка списка полей для отображения в таблице.
    list_display = ['title', 'subject', 'created']

    # Настройка полей для фильтрации данных.
    list_filter = ['created', 'subject']

    # Настройка полей для поиска данных.
    search_fields = ['title', 'overview']

    # Настройка полей с предустановленными значениями.
    prepopulated_fields = {'slug': ('title',)}

    # Настройка инлайновых админ-виджетов.
    inlines = [ModuleInline]
