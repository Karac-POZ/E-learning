# Импортируем необходимые библиотеки.
# Для работы с объектами и перенаправлением страницы.
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse  # Для создания обратной ссылки.

# Импортируем модель курса из файла models.py.
from .models import Course  # Модель курса.


# Функция-мидлвар для определения поддомена и перенаправления на страницу курса.
def subdomain_course_middleware(get_response):
    """
    Функция-мидлвар для определения поддомена и перенаправления на страницу курса.

    :param get_response: Функция, возвращающая HTTP-ответ.
    :return: Middleware функция.
    """

    # Получаем хост из запроса и разбиваем его на части домена и субдомен.
    def middleware(request):
        host_parts = request.get_host().split('.')

        # Если поддомен не равен 'www', то берем первый элемент как ID курса и получаем объект курса из базы данных.
        if len(host_parts) > 2 and host_parts[0] != 'www':
            course = get_object_or_404(Course, slug=host_parts[0])

            # Создаем обратную ссылку на страницу курса.
            course_url = reverse('course_detail', args=[course.slug])

            # Создаем URL с поддоменом и перенаправляем на страницу курса.
            url = '{}://{}{}'.format(
                request.scheme, '.'.join(host_parts[1:]), course_url
            )
            return redirect(url)

        # Если поддомен равен 'www', то берем вторые элемент как ID курса и получаем объект курса из базы данных.
        elif len(host_parts) > 2 and host_parts[0] == 'www':
            course = get_object_or_404(Course, slug=host_parts[1])

            # Создаем обратную ссылку на страницу курса.
            course_url = reverse('course_detail', args=[course.slug])

            # Создаем URL с поддоменом и перенаправляем на страницу курса.
            url = '{}://{}{}'.format(
                request.scheme, '.'.join(host_parts[2:]), course_url
            )
            return redirect(url)

        # Если поддомена нет, то возвращаем HTTP-ответ от функции get_response.
        response = get_response(request)
        return response

    # Возвращаем middleware функцию.
    return middleware
