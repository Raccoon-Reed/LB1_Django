from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва категорії')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Опис')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Зміст')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Категорія'
    )
    # Автор статті — прив'язаний до User
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публікації')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редагування')
    is_published = models.BooleanField(default=True, verbose_name='Опубліковано')

    class Meta:
        verbose_name = 'Стаття'
        verbose_name_plural = 'Статті'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'pk': self.pk})

    def can_edit(self, user):
        """Перевірка: чи може користувач редагувати статтю."""
        if not user.is_authenticated:
            return False
        return user == self.author or user.is_staff or user.is_superuser

    def can_delete(self, user):
        """Перевірка: чи може користувач видалити статтю."""
        return self.can_edit(user)


class UserProfile(models.Model):
    """Розширений профіль користувача з роллю."""

    ROLE_READER = 'reader'
    ROLE_AUTHOR = 'author'
    ROLE_MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (ROLE_READER, 'Читач'),
        (ROLE_AUTHOR, 'Автор'),
        (ROLE_MODERATOR, 'Модератор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
        verbose_name='Роль'
    )
    bio = models.TextField(blank=True, verbose_name='Про себе')
    avatar_url = models.URLField(blank=True, verbose_name='URL аватара')

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    def can_create_article(self):
        return self.role in [self.ROLE_AUTHOR, self.ROLE_MODERATOR] or self.user.is_staff

    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR or self.user.is_staff


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Стаття'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='comments',
        verbose_name='Автор'
    )
    author_name = models.CharField(max_length=100, verbose_name="Ім'я автора", blank=True)
    text = models.TextField(verbose_name='Текст коментаря')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата коментаря')

    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_author()} → {self.article.title}'

    def get_author(self):
        if self.author:
            return self.author.username
        return self.author_name or 'Анонім'

    def can_delete(self, user):
        if not user.is_authenticated:
            return False
        return user == self.author or user.is_staff or user.is_superuser
