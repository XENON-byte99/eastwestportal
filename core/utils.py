from core.models import Notification
from django.contrib.auth import get_user_model
from django.db.models import Q

def send_portal_notification(recipient, title, message, notification_type='system', link=None, sender=None):
    """Safely dispatches internal database notifications to a single user."""
    try:
        return Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link or '#'
        )
    except Exception as e:
        print(f"Failed to dispatch notification: {str(e)}")
        return None

def notify_admins(title, message, notification_type='system', link=None, sender=None):
    """Safely dispatches a broadcast to all staff/admin configurations."""
    User = get_user_model()
    admins = User.objects.filter(Q(is_staff=True) | Q(role='admin') | Q(is_superuser=True)).distinct()
    
    notifications = []
    for admin in admins:
        notifications.append(
            Notification(
                recipient=admin,
                sender=sender,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link or '#'
            )
        )
    if notifications:
        Notification.objects.bulk_create(notifications)
