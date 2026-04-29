from django.contrib import admin
from .models import Course, Material


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'created_at')
    search_fields = ('code', 'name', 'department')
    list_filter = ('department',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'faculty', 'material_type', 'is_approved', 'uploaded_by')
    list_filter = ('is_approved', 'material_type', 'course')
    search_fields = ('title', 'description', 'course__name', 'course__code', 'faculty__first_name', 'faculty__last_name')
    actions = ['approve_materials']

    def approve_materials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_materials.short_description = "Approve selected materials"
