import json

# Импорт асинхронного вебсокета-консумера из Channels
from channels.generic.websocket import AsyncWebsocketConsumer
# Импорт функции для работы с временем из Django
from django.utils import timezone

from chat.models import Message  # Импорт модели сообщения из приложения чата


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Класс, отвечающий за обмен данными между пользователями в режиме реального времени через WebSocket.

    Атрибуты:
        user (User): Текущий пользователь.
        id (int): Идентификатор курса, обсуждаемого в чате.
        room_group_name (str): Имя группы для широковещания сообщений клиентам.
    """

    async def connect(self):
        """
        Вызывается при подключении клиента к этому WebSocket-консуму.

        Обрабатывает добавление клиента в соответствующую группу чата и принятие соединения.
        """
        self.user = self.scope['user']  # Получение текущего пользователя из scope
        # Получение идентификатора курса из scope
        self.id = self.scope['url_route']['kwargs']['course_id']
        # Составление имени группы для широковещания
        self.room_group_name = f'chat_{self.id}'
        await self.channel_layer.group_add(  # Добавление клиента в группу
            self.room_group_name, self.channel_name
        )
        await self.accept()  # Принятие соединения

    async def disconnect(self, close_code):
        """
        Вызывается при разрыве соединения клиента с этим WebSocket-консумом.

        Обрабатывает удаление клиента из соответствующей группы чата.
        """
        await self.channel_layer.group_discard(  # Удаление клиента из группы
            self.room_group_name, self.channel_name
        )

    async def persist_message(self, message):
        """
        Сохраняет сообщение в базе данных при его отправке.

        Аргументы:
            message (str): Текстовое содержание сообщения.
        """
        await Message.objects.acreate(  # Создание записи в модели сообщений с указанными атрибутами
            user=self.user, course_id=self.id, content=message
        )

    async def receive(self, text_data):
        """
        Вызывается при получении текстовых данных от клиента.

        Обрабатывает отправку сообщения в соответствующую группу и сохранение его в базе данных.
        """
        text_data_json = json.loads(
            text_data)  # Получение JSON-объекта из текстовых данных
        message = text_data_json['message']  # Извлечение содержания сообщения
        now = timezone.now()  # Получение текущего времени
        await self.channel_layer.group_send(  # Отправка сообщения в соответствующую группу
            self.room_group_name,
            {
                'type': 'chat_message',  # Тип события (сообщения чата)
                'message': message,  # Содержание сообщения
                'user': self.user.username,  # Имя пользователя отправителя
                'datetime': now.isoformat(),  # Время отправки в формате ISO
            },
        )
        # Сохранение сообщения в базе данных
        await self.persist_message(message)

    async def chat_message(self, event):
        """
        Вызывается при получении события чата.

        Обрабатывает отправку сообщения клиентам.
        """
        await self.send(text_data=json.dumps(event))  # Отправка сообщения в клиенты
