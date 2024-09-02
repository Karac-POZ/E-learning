from django.contrib.auth.models import User  # Импортируем модель User из Django
# Используем GenericForeignKey для связки с ContentTypes
from django.contrib.contenttypes.fields import GenericForeignKey
# Используем ContentType для определения модели контента
from django.contrib.contenttypes.models import ContentType
# Используем стандартные функции Django для работы с базой данных
from django.db import models
# Используем функцию render_to_string из template-loader для рендеринга шаблонов
from django.template.loader import render_to_string

# Импортируем поле OrderField из файла fields.py, которое определяет порядок элемента в модели
from .fields import OrderField


class Subject(models.Model):  # Класс для хранения информации о предметах
    title = models.CharField(max_length=200)  # Поле для названия предмета
    # Поле для слага предмета
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:  # Метакласс для настройки поведения модели
        ordering = ['title']  # Порядок вывода предметов в списке

    def __str__(self):  # Функция для возвращения строки с названием предмета
        return self.title


class Course(models.Model):  # Класс для хранения информации о курсах
    owner = models.ForeignKey(  # Поле для связки с владельцем курса
        User, related_name='courses_created', on_delete=models.CASCADE
    )  # Владелец курса
    subject = models.ForeignKey(  # Поле для связи с предметом курса
        Subject, related_name='courses', on_delete=models.CASCADE
    )  # Предмет курса
    title = models.CharField(max_length=200)  # Название курса
    slug = models.SlugField(max_length=200, unique=True)  # Слаг курса
    overview = models.TextField()  # Описание курса
    created = models.DateTimeField(auto_now_add=True)  # Дата создания курса
    students = models.ManyToManyField(  # Поле для связи с участвующими студентами
        User, related_name='courses_joined', blank=True
    )  # Участвующие студенты

    class Meta:  # Метакласс для настройки поведения модели
        ordering = ['-created']  # Порядок вывода курсов по дате создания

    def __str__(self):  # Функция для возвращения строки с названием курса
        return self.title


class Module(models.Model):  # Класс для хранения информации о модулях курса
    course = models.ForeignKey(  # Поле для связи с курсом, которому принадлежит модуль
        Course, related_name='modules', on_delete=models.CASCADE
    )  # Курс, которому принадлежит модуль
    title = models.CharField(max_length=200)  # Название модуля
    description = models.TextField(blank=True)  # Описание модуля
    # Порядок вывода модулей
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:  # Метакласс для настройки поведения модели
        ordering = ['order']  # Порядок вывода модулей по порядку

    def __str__(self):  # Функция для возвращения строки с названием модуля и порядковым номером
        return f"{self.title} (#{self.order})"


class Content(models.Model):  # Класс для хранения информации о контенте модулей курса
    content_type = models.ForeignKey(  # Поле для связи с типом контента
        ContentType, on_delete=models.CASCADE
    )  # Тип контента
    # ID объекта, которому принадлежит контент
    object_id = models.PositiveIntegerField()
    # Контент, связанный с определенным типом и ID объекта
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:  # Метакласс для настройки поведения модели
        ordering = ['order']  # Порядок вывода контента по порядку


# Базовый класс для хранения информации об элементах, связанных с определенным типом контента
class ItemBase(models.Model):
    owner = models.ForeignKey(  # Поле для связи с владельцем элемента
        User, related_name='%(class)s_related', on_delete=models.CASCADE
    )  # Владелец элемента
    title = models.CharField(max_length=250)  # Название элемента
    created = models.DateTimeField(auto_now_add=True)  # Дата создания элемента
    # Дата последнего обновления элемента
    updated = models.DateTimeField(auto_now=True)

    class Meta:  # Метакласс для настройки поведения модели
        abstract = True  # Этот класс является базовым и не может использоваться напрямую

    def __str__(self):  # Функция для возвращения строки с названием элемента
        return self.title

    def render(self):  # Функция для рендеринга шаблона элемента
        return render_to_string(  # Используем функцию render_to_string из template-loader
            # Шаблон элемента, который нужно подставить в контент
            f'courses/content/{self._meta.model_name}.html',
            {'item': self}  # Словарь для передачи данных в шаблон
        )


class Text(ItemBase):  # Класс для хранения информации о тексте элемента
    content = models.TextField()  # Содержимое текста


class File(ItemBase):  # Класс для хранения информации о файле элемента
    file = models.FileField(upload_to='files')  # Путь к файлу


class Image(ItemBase):  # Класс для хранения информации об изображении элемента
    file = models.FileField(upload_to='images')  # Путь к изображению


class Video(ItemBase):  # Класс для хранения информации о видео элемента
    url = models.URLField()  # Ссылка на видео
