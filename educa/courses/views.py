# Импорт необходимых миксинов, классов представлений и моделей
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.cache import cache
from django.db.models import Count
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from students.forms import CourseEnrollForm

from .forms import ModuleFormSet
from .models import Content, Course, Module, Subject


class OwnerMixin:
    """
    Миксин для фильтрации объектов по текущему пользователю.
    Фильтрует queryset по полю 'owner', чтобы отобразить только те объекты, которые принадлежат текущему пользователю.
    """

    def get_queryset(self):
        # Фильтрация объектов по владельцу
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    """
    Миксин для автоматического назначения текущего пользователя владельцем объекта при сохранении формы.
    Устанавливает значение поля 'owner' текущим пользователем перед сохранением объекта.
    """

    def form_valid(self, form):
        # Устанавливаем текущего пользователя владельцем объекта перед сохранением формы
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Миксин для управления курсами, включает фильтрацию по владельцу и проверку прав доступа.
    Определяет модель курса и поля формы для редактирования.
    """
    model = Course  # Модель курса
    fields = ['subject', 'title', 'slug', 'overview']  # Поля формы курса
    # URL для перенаправления после успешного выполнения действия
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """
    Миксин для редактирования курсов.
    Определяет шаблон формы для создания и обновления курса.
    """
    template_name = 'courses/manage/course/form.html'  # Шаблон формы курса


class ManageCourseListView(OwnerCourseMixin, ListView):
    """
    Представление для отображения списка курсов, принадлежащих текущему пользователю.
    Проверяет права доступа на просмотр курсов.
    """
    template_name = 'courses/manage/course/list.html'  # Шаблон списка курсов
    # Права доступа для просмотра курсов
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """
    Представление для создания нового курса.
    Проверяет права доступа на добавление курсов.
    """
    permission_required = 'courses.add_course'  # Права доступа для создания курсов


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """
    Представление для обновления информации о курсе.
    Проверяет права доступа на изменение курсов.
    """
    permission_required = 'courses.change_course'  # Права доступа для изменения курсов


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """
    Представление для удаления курса.
    Проверяет права доступа на удаление курсов.
    """
    template_name = 'courses/manage/course/delete.html'  # Шаблон для подтверждения удаления курса
    # Права доступа для удаления курсов
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """
    Представление для управления модулями курса с помощью формсета.
    Позволяет добавлять, изменять и удалять модули курса.
    """
    template_name = 'courses/manage/module/formset.html'  # Шаблон для формы модулей
    course = None  # Переменная для хранения текущего курса

    def get_formset(self, data=None):
        """
        Метод для получения формсета модулей.
        """
        # Возвращает формсет для модуля курса
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        """
        Метод для обработки запросов к представлению, проверяет доступность курса для текущего пользователя.
        """
        # Получаем курс по идентификатору и проверяем, что он принадлежит текущему пользователю
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        """
        Метод для отображения формы с модулями.
        """
        # Отображает форму для редактирования модулей курса
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        """
        Метод для обработки отправки формы с модулями.
        Сохраняет изменения, если форма валидна.
        """
        # Обработка отправленной формы и сохранение изменений
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    """
    Представление для создания или обновления содержимого модуля (текст, видео, изображение, файл).
    Определяет модель содержимого и форму на основе переданных параметров.
    """
    module = None  # Переменная для хранения текущего модуля
    model = None  # Модель содержимого
    obj = None  # Объект содержимого
    template_name = 'courses/manage/content/form.html'  # Шаблон для формы содержимого

    def get_model(self, model_name):
        """
        Метод для получения модели содержимого по названию.
        """
        # Возвращает модель содержимого по имени, если она допустима
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        """
        Метод для создания формы на основе модели.
        """
        # Создает форму на основе переданной модели
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        """
        Метод для обработки запросов, определяет модуль и объект содержимого.
        """
        # Получает текущий модуль и объект содержимого, если он указан
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        """
        Метод для отображения формы содержимого.
        """
        # Отображает форму для создания или редактирования содержимого
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        """
        Метод для обработки отправки формы содержимого.
        Сохраняет объект, если форма валидна.
        """
        # Обработка отправленной формы и сохранение объекта содержимого
        form = self.get_form(self.model, instance=self.obj,
                             data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # Создание нового содержимого
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    """
    Представление для удаления содержимого модуля.
    Удаляет объект содержимого и перенаправляет на список содержимого модуля.
    """

    def post(self, request, id):
        # Получаем объект содержимого по ID и проверяем, что он принадлежит курсу текущего пользователя
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user)
        module = content.module  # Сохраняем ссылку на модуль для перенаправления
        content.item.delete()  # Удаляем связанный объект содержимого
        content.delete()  # Удаляем сам объект содержимого
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    """
    Представление для отображения списка содержимого модуля.
    Позволяет просматривать все элементы содержимого, связанные с модулем.
    """
    # Шаблон для отображения списка содержимого модуля
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        """
        Метод для отображения списка содержимого модуля.
        """
        # Получаем модуль по идентификатору и проверяем, что он принадлежит курсу текущего пользователя
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        # Возвращаем ответ с модулем для отображения содержимого
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """
    Представление для изменения порядка модулей с использованием AJAX.
    Получает данные в формате JSON и обновляет порядок модулей.
    """

    def post(self, request):
        """
        Метод для обработки AJAX-запроса на изменение порядка модулей.
        """
        # Обновляем порядок модулей на основе переданных данных JSON
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id, course__owner=request.user).update(order=order)
        # Возвращаем ответ с подтверждением успешного сохранения
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """
    Представление для изменения порядка содержимого с использованием AJAX.
    Получает данные в формате JSON и обновляет порядок элементов содержимого.
    """

    def post(self, request):
        """
        Метод для обработки AJAX-запроса на изменение порядка содержимого.
        """
        # Обновляем порядок элементов содержимого на основе переданных данных JSON
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__owner=request.user).update(order=order)
        # Возвращаем ответ с подтверждением успешного сохранения
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    """
    Представление для отображения списка курсов.
    Фильтрует курсы по предмету, если указан, и использует кэширование для улучшения производительности.
    """
    model = Course  # Модель курса
    # Шаблон для отображения списка курсов
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        """
        Метод для отображения списка курсов, с возможностью фильтрации по предмету.
        """
        # Кэширование списка всех предметов
        subjects = cache.get('all_subjects')
        if not subjects:
            # Если предметы не закэшированы, выполняем запрос и сохраняем в кэш
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)

        # Если указан предмет, фильтруем курсы по этому предмету
        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            all_courses = all_courses.filter(subject=subject)

        # Кэширование списка курсов
        cache.set(f'all_courses_{
                  subject.slug if subject else "all"}', all_courses)

        # Возвращаем ответ с курсами и предметами для отображения
        return self.render_to_response({'subjects': subjects, 'subject': subject, 'courses': all_courses})


class CourseDetailView(DetailView):
    """
    Представление для отображения подробной информации о курсе.
    """
    model = Course  # Модель курса
    # Шаблон для отображения деталей курса
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        """
        Метод для получения дополнительных данных для шаблона.
        """
        context = super().get_context_data(**kwargs)
        # Добавляем форму для записи на курс
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object})
        return context
