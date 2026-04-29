from .models import Announcement

def announcements_processor(request):
    """Makes the latest 5 active announcements available globally."""
    latest_announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
    return {
        'global_announcements': latest_announcements
    }
