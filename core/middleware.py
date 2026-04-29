from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_URLS = [
    '/accounts/',
    '/admin/',
    '/static/',
    '/media/',
    '/favicon.ico',
    '/core/pending/',
    '/core/logout/',
    '/core/api/',
]




class ApprovalRequiredMiddleware:
    # ... (same as before)
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser and not request.user.is_staff:
                if not getattr(request.user, 'is_approved', True):
                    pending_url = reverse('core:pending_approval')
                    current_path = request.path
                    is_exempt = any(current_path.startswith(url) for url in EXEMPT_URLS)
                    if not is_exempt and current_path != pending_url:
                        return redirect(pending_url)
        return self.get_response(request)


class EnrollmentRequiredMiddleware:
    """
    Ensure students have selected courses for the current semester.
    If not, redirect to enrollment page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
            if request.user.is_student:
                from core.models import Enrollment
                from django.utils import timezone
                
                # Simple logic for current semester
                now = timezone.now()
                month = now.month
                year = now.year
                if month <= 4: semester = 'Spring'
                elif month <= 8: semester = 'Summer'
                else: semester = 'Fall'

                enroll_url = reverse('core:enrollment')
                current_path = request.path
                is_exempt = any(current_path.startswith(url) for url in EXEMPT_URLS)
                
                if not is_exempt and current_path != enroll_url:
                    has_enrollment = Enrollment.objects.filter(student=request.user, semester=semester, year=year).exists()
                    if not has_enrollment:
                        return redirect(enroll_url)

        return self.get_response(request)

class ExemptCSRFMiddleware:
    """
    Temporary middleware to bypass CSRF enforcement on login
    to verify if the 403 error is CSRF related.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/accounts/login/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)
