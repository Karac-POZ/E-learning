from courses.models import Course
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    """
    Представление для регистрации нового студента. 

    Использует форму регистрации пользователя `UserCreationForm` и при успешной регистрации 
    автоматически аутентифицирует и логирует пользователя в системе.
    """
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        """
        Метод вызывается при успешной валидации формы. 

        Выполняет аутентификацию и вход нового пользователя после успешной регистрации.

        :param form: Валидная форма регистрации пользователя.
        :return: Результат выполнения родительского метода form_valid.
        """
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'], password=cd['password1']
        )
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    """
    Представление для записи студента на курс. 

    Пользователь должен быть аутентифицирован для доступа к этому представлению. 
    После успешной записи курс добавляется в список курсов студента.
    """
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        """
        Метод вызывается при успешной валидации формы. 

        Добавляет текущего пользователя в список студентов выбранного курса.

        :param form: Валидная форма записи на курс.
        :return: Результат выполнения родительского метода form_valid.
        """
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """
        Метод возвращает URL, на который будет перенаправлен пользователь после успешной записи на курс.

        :return: URL-адрес страницы с деталями выбранного курса.
        """
        return reverse_lazy(
            'student_course_detail', args=[self.course.id]
        )


class StudentCourseListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка курсов, на которые записан текущий пользователь. 

    Пользователь должен быть аутентифицирован для доступа к этому представлению.
    """
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        """
        Метод возвращает queryset курсов, на которые записан текущий пользователь.

        :return: QuerySet с курсами, на которые записан текущий пользователь.
        """
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей конкретного курса. 

    Пользователь должен быть аутентифицирован для доступа к этому представлению. 
    Показывает детали курса и текущий модуль, если он указан в URL.
    """
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        """
        Метод возвращает queryset курсов, на которые записан текущий пользователь.

        :return: QuerySet с курсами, на которые записан текущий пользователь.
        """
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        """
        Метод добавляет дополнительные данные в контекст шаблона.

        Если в URL указан параметр `module_id`, добавляет текущий модуль в контекст.
        В противном случае, добавляет первый модуль курса в контекст.

        :param kwargs: Дополнительные параметры контекста.
        :return: Обновленный словарь контекста.
        """
        context = super().get_context_data(**kwargs)
        # Получаем объект курса
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # Получаем текущий модуль
            context['module'] = course.modules.get(
                id=self.kwargs['module_id']
            )
        else:
            # Получаем первый модуль
            context['module'] = course.modules.all()[0]
        return context
