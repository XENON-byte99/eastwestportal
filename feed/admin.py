from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_by', 'is_approved', 'likes', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('uploaded_by__email', 'content')
    actions = ['approve_posts']

    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'uploaded_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('uploaded_by__email', 'text')
