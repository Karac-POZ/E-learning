from django.conf import settings  # Импорт настроек Django из файла settings.py
from django.db import models  # Импорт моделей базы данных из пакета django.db


class Message(models.Model):
    """
    Модель для хранения сообщений пользователей в чате.

    Атрибуты:
        user (User): Пользователь, отправивший сообщение.
        course (Course): Курс, на котором происходит обсуждение.
        content (str): Содержание сообщения.
        sent_on (datetime): Время отправки сообщения.
    """

    user = models.ForeignKey(  # Член, связывающий модель с User модели
        settings.AUTH_USER_MODEL,  # Идентификатор модели пользователя из настроек Django
        on_delete=models.PROTECT,  # Установка удаления при удалении родительского элемента
        related_name='chat_messages',  # Название отношения к этому объекту в User модели
    )
    course = models.ForeignKey(  # Член, связывающий модель с Course моделью
        'courses.Course',  # Идентификатор модели курса из модуля courses
        on_delete=models.PROTECT,  # Установка удаления при удалении родительского элемента
        related_name='chat_messages',  # Название отношения к этому объекту в Course модели
    )
    content = models.TextField()  # Поле для хранения содержания сообщения
    sent_on = models.DateTimeField(  # Поле для хранения времени отправки сообщения
        auto_now_add=True,  # Установка времени создания записи при ее добавлении
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта модели.

        Returns:
            str: Строковое представление объекта модели.
        """
        return f'{self.user} on {self.course} at {self.sent_on}'  # Возвращение строки в формате user на course в time
