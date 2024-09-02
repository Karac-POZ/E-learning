# Импортируем необходимые библиотеки для работы с базой данных.
# Для исключения объекта, если он не существует в базе данных.
from django.core.exceptions import ObjectDoesNotExist
from django.db import models  # Для работы с моделями и полями.


class OrderField(models.PositiveIntegerField):
    """
    Класс для создания полей заказа.

    Поля:
        for_fields (list): Список полей для определения последнего порядкового номера.
    """

    def __init__(self, for_fields=None, *args, **kwargs):
        """
        Метод инициализации класса OrderField.

        Параметры:
            self.for_fields (list): Список полей для определения последнего порядкового номера.
        """
        self.for_fields = for_fields  # Хранение списка полей в атрибуте class.
        # Вызов метода инициализации родительского класса.
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Метод для определения последнего порядкового номера перед сохранением модели.

        Параметры:
            self.model (Model): Модель базы данных.
            self.attname (str): Имя атрибута поля в модели.
            self.for_fields (list): Список полей для определения последнего порядкового номера.

        Возвращает:
            int: Последний порядковый номер + 1, если он существует. Иначе 0.
        """
        if getattr(model_instance, self.attname) is None:
            try:
                # Получение всех объектов модели.
                qs = self.model.objects.all()
                if self.for_fields:
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }  # Создание словаря для фильтрации по полям.
                    qs = qs.filter(**query)  # Фильтрация объектов по полям.
                # Получение последнего объекта в сортировке по полю.
                last_item = qs.latest(self.attname)
                # Подсчет последнего порядкового номера + 1.
                value = getattr(last_item, self.attname) + 1
            except ObjectDoesNotExist:
                # Инициализация значение 0, если последний объект не существует.
                value = 0
            # Установка значения в атрибуте модели.
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)
