from django.db import models
from django.utils import timezone
# модель User берем из встроенной платформы аутентификации
from django.contrib.auth.models import User

from django.urls import reverse


# objects - менеджер моделей по умолчанию
class PublishedManager(models.Manager):
    # пользовательский менеджер, который получает все опубликованные посты
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):
        # Для создания поля с выбором значений объявим класс Status с двумя атрибутами
        # "DF" значение в таблице, "Draft" удобочитаемое имя, которое будет в select
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # Foreign Key - вторичный ключ (первичный ключ в Django моделях не указывается)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # по умолчанию обявляем полю status значение ЧЕРНОВИК
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT)

    # если мы добавляем кастомный менеджер, то менеджер по умолчанию необходимо явно указать
    objects = models.Manager()  # менеджер по умолчанию
    published = PublishedManager()  # кастомный менеджер

    class Meta:
        # сортируем записи по полю publish в порядке убывания
        ordering = ['-publish']
        indexes = [
            # создаем индекс по полю publish для ускорения запросов
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    # получаем абсолютную ссылку на объект базы
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day,
                                                 self.slug])


class Comment(models.Model):
    # модель для хранения комментариев пользователей
    
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='comments')
    # поле пост, является вторичным ключем модели Post

    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
