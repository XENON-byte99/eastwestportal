from django.contrib import admin
from .models import ResearchArea, Paper, Capstone


class PaperInline(admin.TabularInline):
    model = Paper
    extra = 1


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ('research_area', 'lead_faculty', 'created_at')
    search_fields = ('research_area', 'lead_faculty__email')
    inlines = [PaperInline]


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'field', 'passing_year', 'semester', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'passing_year', 'semester', 'research_area')
    search_fields = ('title', 'authors', 'field', 'faculty_name', 'uploaded_by__email')
    list_editable = ('is_approved',)


@admin.register(Capstone)
class CapstoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'field', 'passing_year', 'semester', 'status', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'status', 'passing_year', 'semester')
    search_fields = ('title', 'team_members', 'field', 'faculty_name', 'uploaded_by__email')
    list_editable = ('status', 'is_approved')
