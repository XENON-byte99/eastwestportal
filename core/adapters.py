from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from core.utils import notify_admins



ALLOWED_DOMAIN = 'ewubd.edu'


class EWUAccountAdapter(DefaultAccountAdapter):
    """
    Restricts email/password signups to @ewubd.edu addresses.
    New accounts are created with is_approved=False and must be
    approved by admin before they can log in.
    """

    def clean_email(self, email):

        email = super().clean_email(email)
        domain = email.split('@')[-1].lower()
        if domain != ALLOWED_DOMAIN:
            raise ValidationError(
                f"Only @{ALLOWED_DOMAIN} email addresses are allowed to register."
            )
        return email

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_approved = False
        user.is_active = True   # Active but not approved — middleware blocks them
        if commit:
            user.save()
            notify_admins(
                title="New User Registration",
                message=f"A new user ({user.email}) has registered and requires approval.",
                notification_type="system",
                link="/core/manage/users/"
            )
        return user


    def is_open_for_signup(self, request):
        return True


class EWUSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Restricts Google OAuth logins to @ewubd.edu addresses.
    New social accounts also require admin approval.
    """

    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '')
        domain = email.split('@')[-1].lower()
        if domain != ALLOWED_DOMAIN:
            raise ValidationError(
                f"Only @{ALLOWED_DOMAIN} Google accounts are allowed."
            )
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Called right after a successful OAuth handshake but before
        the user is created/logged in. Validate domain here too.
        """
        email = sociallogin.account.extra_data.get('email', '')
        domain = email.split('@')[-1].lower()
        if domain != ALLOWED_DOMAIN:
            from django.shortcuts import redirect
            from allauth.account.models import EmailAddress
            raise ValidationError(
                f"Only @{ALLOWED_DOMAIN} Google accounts are permitted."
            )

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not user.is_superuser:
            user.is_approved = False
            user.save()
            notify_admins(
                title="New Google OAuth Registration",
                message=f"A new user ({user.email}) has signed up via Google and requires verification.",
                notification_type="system",
                link="/core/manage/users/"
            )
        return user

