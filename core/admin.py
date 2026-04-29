from django.contrib import admin
from django.utils import timezone
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'department', 'is_approved', 'is_active', 'date_joined')
    list_filter = ('is_approved', 'role', 'is_active', 'is_staff')
    list_editable = ('is_approved',)
    search_fields = ('email', 'first_name', 'last_name', 'student_id', 'department')
    ordering = ('is_approved', '-date_joined')
    actions = ['approve_users', 'reject_users']
    readonly_fields = ('date_joined', 'last_login', 'date_approved')

    fieldsets = (
        ('Account', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'bio', 'profile_picture')
        }),
        ('University Info', {
            'fields': ('role', 'department', 'student_id')
        }),
        ('Access Control', {
            'fields': ('is_approved', 'is_active', 'is_staff', 'is_superuser', 'date_approved'),
            'classes': ('wide',),
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login'),
        }),
    )

    def approve_users(self, request, queryset):
        updated = queryset.update(is_approved=True, date_approved=timezone.now())
        self.message_user(request, f'{updated} user(s) approved successfully.')
    approve_users.short_description = '✅ Approve selected users'

    def reject_users(self, request, queryset):
        updated = queryset.update(is_approved=False, is_active=False)
        self.message_user(request, f'{updated} user(s) rejected and deactivated.')
    reject_users.short_description = '❌ Reject & deactivate selected users'
