from django.db.models import Count
from rest_framework import serializers

from courses.models import Content, Course, Module, Subject


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Subject.

    Поля:
        - total_courses: общее количество курсов для этого предмета.
        - popular_courses: три самых популярных курса по этому предмету.

    Файлдс:
        - id
        - title
        - slug
        - total_courses
        - popular_courses
    """
    total_courses = serializers.IntegerField()
    popular_courses = serializers.SerializerMethodField()

    def get_popular_courses(self, obj):
        """
        Получает три самых популярных курса по этому предмету.

        :param obj: экземпляр модели Subject.
        :return: список строк формата "Название курса (Количество студентов)".
        """
        courses = obj.courses.annotate(
            total_students=Count('students')
        ).order_by('-total_students')[:3]
        return [
            f'{c.title} ({c.total_students} students)' for c in courses
        ]

    class Meta:
        model = Subject
        fields = [
            'id',
            'title',
            'slug',
            'total_courses',
            'popular_courses',
        ]


class ModuleSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Module.

    Поля:
        - order: порядковый номер модуля.
        - title: название модуля.
        - description: описание модуля.

    Файлдс:
        - order
        - title
        - description
    """
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Course.

    Поля:
        - id: уникальный идентификатор курса.
        - subject: предмет, на который рассчитан курс.
        - title: название курса.
        - slug: уникальная строка-идентификатор курса.
        - overview: краткое описание курса.
        - created: дата создания курса.
        - owner: владелец курса.
        - modules: список модулей, входящих в состав курса.
    """
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules',
        ]


class ItemRelatedField(serializers.RelatedField):
    """
    Поле, сериализирующее связь между Content и другой моделью.
    """

    def to_representation(self, value):
        return value.render()


class ContentSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Content.

    Поля:
        - order: порядковый номер содержания.
        - item: экземпляр другой модели, связанной с content.
    """
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleWithContentsSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Module с вложенными содержаниями.

    Поля:
        - order: порядковый номер модуля.
        - title: название модуля.
        - description: описание модуля.
        - contents: список содержаний, входящих в состав модуля.
    """
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']


class CourseWithContentsSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Course с вложенными модулями и содержаниями.

    Поля:
        - id: уникальный идентификатор курса.
        - subject: предмет, на который рассчитан курс.
        - title: название курса.
        - slug: уникальная строка-идентификатор курса.
        - overview: краткое описание курса.
        - created: дата создания курса.
        - owner: владелец курса.
        - modules: список модулей, входящих в состав курса.
    """
    modules = ModuleWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules',
        ]
