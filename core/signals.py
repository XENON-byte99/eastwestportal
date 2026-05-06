from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification
from datetime import datetime

@receiver(post_save, sender=Notification)
def trigger_external_notification(sender, instance, created, **kwargs):
    """
    Automatically sends email/whatsapp alerts when a new Notification is created in the database.
    This ensures that even if a view creates a Notification directly, the user still gets an external alert.
    """
    if created:
        recipient = instance.recipient
        if not recipient or not recipient.email:
            return

        # Skip email for certain types if needed, but for now we send all
        try:
            context = {
                'title': instance.title,
                'message': instance.message,
                'link': instance.link,
                'category': instance.get_notification_type_display() if hasattr(instance, 'get_notification_type_display') else instance.notification_type,
                'year': datetime.now().year,
                'site_url': 'http://localhost:8000' # Change to settings.SITE_URL in production
            }
            html_message = render_to_string('core/emails/notification.html', context)
            
            send_mail(
                subject=f"[{settings.PORTAL_NAME}] {instance.title}",
                message=instance.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_message,
                fail_silently=True
            )
            print(f"DEBUG: Multi-channel notification sent to {recipient.email}")
        except Exception as e:
            print(f"ERROR: Failed to send external notification: {str(e)}")
