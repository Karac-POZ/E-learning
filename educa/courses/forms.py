# Импортируем необходимые библиотеки для работы с формами.
# Для создания фиксированной формы.
from django.forms.models import inlineformset_factory

# Импортируем модели из файла models.py.
from .models import Course, Module  # Модель курса и модуля.


# Создаем форму для модулей в курсе с возможностью удаления и дополнительными полями title и description.
ModuleFormSet = inlineformset_factory(
    Course,  # Модель-родитель для создания формы.
    Module,  # Модель-деталь для создания формы.
    fields=['title', 'description'],  # Поля в форме: title и description.
    extra=2,  # Количество дополнительных форм в наборе.
    can_delete=True,  # Возможность удаления записей в форме.
)
