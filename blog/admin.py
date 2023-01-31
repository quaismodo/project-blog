from django.contrib import admin
from .models import Post, Comment

# admin.site.register(Post)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # list_display - поля которые отображаются в списке постов
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    # list_filter - создает фильтр в списке постов по указанным полям
    list_filter = ['status', 'created', 'publish', 'author']
    # search_fields - создает поле поиска и ищет по указанным полям
    search_fields = ['title', 'body']
    # prepopulated_fields - автоматически создает поле slug на основе title
    prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields - строковое представление поля author, вместо имя пользователя указывается id поле
    raw_id_fields = ['author']
    # date_hierarchy - добавляет навигацию по иерархии дат
    date_hierarchy = 'publish'
    # ordering - сортирует список постов по указанным полям
    ordering = ['status', 'publish']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']