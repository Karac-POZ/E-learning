from django.utils import timezone
from django.db.models import Count
from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User
from django.conf import settings
import datetime


class Command(BaseCommand):
    """
    Команда для отправки напоминаний по электронной почте пользователям, 
    которые зарегистрировались более N дней назад, но не записались ни на один курс.

    Команда принимает необязательный аргумент `--days`, чтобы указать количество дней 
    с момента регистрации. Если аргумент не указан, по умолчанию используется 0, 
    что включает всех пользователей, которые не записались на курсы.
    """
    help = 'Отправляет напоминание по электронной почте пользователям, зарегистрированным более N дней назад и не записавшимся на курсы'

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки в парсер.

        :param parser: Экземпляр парсера аргументов.
        """
        # Добавление необязательного аргумента '--days' для указания количества дней с момента регистрации
        parser.add_argument('--days', dest='days', type=int)

    def handle(self, *args, **options):
        """
        Основной метод, выполняемый при вызове команды.

        Выбирает пользователей, которые зарегистрировались более N дней назад 
        и не записались ни на один курс, и отправляет им напоминания по электронной почте.
        """
        emails = []
        subject = 'Запишитесь на курс'

        # Определяем дату регистрации, до которой будут выбраны пользователи
        date_joined = timezone.now().today() - datetime.timedelta(
            days=options['days'] or 0
        )

        # Выбираем пользователей, у которых нет записей на курсы и которые зарегистрировались до указанной даты
        users = User.objects.annotate(
            course_count=Count('courses_joined')
        ).filter(course_count=0, date_joined__date__lte=date_joined)

        for user in users:
            # Формируем сообщение для каждого пользователя
            message = f"""Здравствуйте, {user.first_name}!
            Мы заметили, что вы пока не записались на наши курсы.
            Возможно, вам будет интересно узнать больше о том, что мы предлагаем.
            Не упустите возможность начать учиться прямо сейчас!
 """

            # Добавляем письмо в список для массовой отправки
            emails.append(
                (
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
            )

        # Отправляем все собранные письма
        send_mass_mail(emails)

        # Выводим сообщение о количестве отправленных напоминаний
        self.stdout.write(f'Отправлено {len(emails)} напоминаний')
