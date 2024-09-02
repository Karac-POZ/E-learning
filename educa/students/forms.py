from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    """
    Форма для записи пользователя на курс. 

    Форма содержит одно скрытое поле `course`, которое отображает список доступных курсов.
    Список курсов заполняется при инициализации формы с использованием всех доступных записей из модели Course.
    """

    # Поле выбора курса, инициализируется пустым queryset, но позже заполняется доступными курсами
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        """
        Инициализатор формы. При создании экземпляра формы, заполняет поле `course`
        списком всех доступных курсов.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """
        # Вызов инициализатора родительского класса
        super(CourseEnrollForm, self).__init__(*args, **kwargs)

        # Заполнение queryset поля 'course' всеми доступными курсами
        self.fields['course'].queryset = Course.objects.all()
