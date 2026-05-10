from django.contrib import admin
from .models import Insight

@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'author', 'created_at')
    list_filter = ('course', 'faculty', 'author')
    search_fields = ('content', 'course__code', 'course__name')
