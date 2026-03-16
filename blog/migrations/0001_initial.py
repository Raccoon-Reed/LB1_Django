from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Назва категорії')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
            ],
            options={'verbose_name': 'Категорія', 'verbose_name_plural': 'Категорії', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Зміст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публікації')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата редагування')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубліковано')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='blog.category', verbose_name='Категорія')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={'verbose_name': 'Стаття', 'verbose_name_plural': 'Статті', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('reader', 'Читач'), ('author', 'Автор'), ('moderator', 'Модератор')], default='reader', max_length=20, verbose_name='Роль')),
                ('bio', models.TextField(blank=True, verbose_name='Про себе')),
                ('avatar_url', models.URLField(blank=True, verbose_name='URL аватара')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Профіль', 'verbose_name_plural': 'Профілі'},
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, max_length=100, verbose_name="Ім'я автора")),
                ('text', models.TextField(verbose_name='Текст коментаря')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата коментаря')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.article', verbose_name='Стаття')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={'verbose_name': 'Коментар', 'verbose_name_plural': 'Коментарі', 'ordering': ['created_at']},
        ),
    ]
