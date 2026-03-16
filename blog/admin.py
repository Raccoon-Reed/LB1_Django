from django.contrib import admin
from .models import Category, Article, Comment, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'user__email']
    list_filter = ['role']
    list_editable = ['role']
    search_fields = ['user__username', 'user__email']

    def user__email(self, obj):
        return obj.user.email
    user__email.short_description = 'Email'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count']
    prepopulated_fields = {'slug': ('name',)}

    def article_count(self, obj):
        return obj.articles.filter(is_published=True).count()
    article_count.short_description = 'Кількість статей'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'author']
    list_editable = ['is_published']
    search_fields = ['title', 'content']
    raw_id_fields = ['author']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['get_author', 'article', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'text']
