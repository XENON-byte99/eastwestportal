from django.contrib import admin
from .models import Listing, ChatMessage


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'uploaded_by', 'price', 'listing_type', 'status', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'status', 'listing_type', 'condition')
    search_fields = ('item_name', 'description', 'uploaded_by__email')
    list_editable = ('status', 'is_approved')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'sender', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__email', 'text')
