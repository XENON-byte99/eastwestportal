from core.models import Notification
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime

def send_portal_notification(recipient, title, message, notification_type='system', link=None, sender=None, send_email=True):
    """
    Safely dispatches internal database notifications to a single user.
    Also handles multi-channel delivery (Email, WhatsApp, etc).
    """
    try:
        # 1. Create DB Notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link or '#'
        )

        # 2. External: Email Notification
        if send_email and recipient.email:
            try:
                context = {
                    'title': title,
                    'message': message,
                    'link': link,
                    'category': notification_type.replace('_', ' ').title(),
                    'year': datetime.now().year,
                    'site_url': 'http://localhost:8000' # In prod, use site domain
                }
                html_message = render_to_string('core/emails/notification.html', context)
                
                send_mail(
                    subject=f"[{settings.PORTAL_NAME}] {title}",
                    message=message, # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception as email_err:
                print(f"Email delivery failed: {str(email_err)}")

        # 3. External: WhatsApp Notification (Placeholder)
        if recipient.whatsapp_number:
            # Here we would integrate with Twilio or another API
            # print(f"Triggering WhatsApp alert to {recipient.whatsapp_number}")
            pass

        return notification
    except Exception as e:
        print(f"Failed to dispatch notification: {str(e)}")
        return None

def notify_admins(title, message, notification_type='system', link=None, sender=None, send_email=True):
    """Safely dispatches a broadcast to all staff/admin configurations."""
    User = get_user_model()
    admins = User.objects.filter(Q(is_staff=True) | Q(role='admin') | Q(is_superuser=True)).distinct()
    
    for admin in admins:
        send_portal_notification(admin, title, message, notification_type, link, sender, send_email)

def bulk_send_notifications(recipients, title, message, notification_type='system', link=None, sender=None):
    """
    Handles large-scale notifications (e.g. for announcements).
    Creates DB records in bulk and handles background email/push alerts.
    """
    notifications = [
        Notification(
            recipient=user,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link or '#'
        ) for user in recipients
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
        
        # Note: In a real production environment, we would queue a Celery task here
        # to send mass emails/push notifications in the background.
        # Example: mass_email_task.delay(user_ids, title, message)
        print(f"DEBUG: Bulk notifications created for {len(recipients)} users.")
