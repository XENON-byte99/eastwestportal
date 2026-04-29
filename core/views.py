from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.apps import apps
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
import json

from feed.models import Post
from materials.models import Material
from marketplace.models import Listing
from projects.models import Paper, Capstone

User = get_user_model()
from .utils import send_portal_notification, notify_admins
def csrf_failure(request, reason=""):
    context = {
        'reason': reason,
        'path': request.path,
        'method': request.method,
        'headers': dict(request.headers),
        'origin': request.headers.get('Origin', 'No Origin'),
        'referer': request.headers.get('Referer', 'No Referer'),
    }
    from django.http import HttpResponse
    import json
    html = f"""
    <html>
    <body>
        <h1>CSRF Verification Failed (Custom Debug)</h1>
        <p><strong>Reason:</strong> {reason}</p>
        <p><strong>Method:</strong> {request.method}</p>
        <p><strong>Path:</strong> {request.path}</p>
        <p><strong>Origin:</strong> {context['origin']}</p>
        <p><strong>Referer:</strong> {context['referer']}</p>
        <hr>
        <h3>All Headers:</h3>
        <pre>{json.dumps(context['headers'], indent=2)}</pre>
    </body>
    </html>
    """
    return HttpResponse(html, status=403)


def is_staff(user):
    return user.is_staff or user.is_superuser


@login_required
def home(request):
    """The separate Dashboard/Stats page."""
    context = {
        'total_posts': Post.objects.filter(is_approved=True).count(),
        'total_materials': Material.objects.filter(is_approved=True).count(),
        'total_listings': Listing.objects.filter(status='active', is_approved=True).count(),
        'total_papers': Paper.objects.filter(is_approved=True).count(),
        'total_capstones': Capstone.objects.filter(is_approved=True).count(),
    }
    return render(request, 'core/home.html', context)


@login_required
@user_passes_test(is_staff)
def manage_users(request):
    """View to render the User/Faculty Management page."""
    return render(request, 'core/manage_users.html')


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST', 'DELETE'])
@user_passes_test(is_staff)
def api_user_manage(request, user_id=None):
    """API for managing portal users (Admin only)."""
    if request.method == 'GET':
        users = User.objects.all().order_by('-date_joined')
        users_data = []
        for u in users:
            users_data.append({
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'role': u.role,
                'is_approved': u.is_approved,
                'date_joined': u.date_joined.strftime("%b %d, %Y"),
                'full_name': u.get_full_name() or u.email,
                'profile_picture': u.profile_picture.url if u.profile_picture else '',
                'id_card_image': u.id_card_image.url if u.id_card_image else '',
                'whatsapp_number': u.whatsapp_number or ''
            })
        return JsonResponse({'users': users_data})

    if request.method == 'POST':
        # Update user status or role
        try:
            body = json.loads(request.body)
            action = body.get('action')

            if action == 'create':
                # ... (existing create logic)
                email = body.get('email', '').strip().lower()
                first_name = body.get('first_name', '').strip()
                last_name = body.get('last_name', '').strip()
                password = body.get('password', 'Portal@2025')
                role = body.get('role', 'student')

                if not email or not first_name:
                    return JsonResponse({'error': 'Email and First Name are required.'}, status=400)
                
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'error': 'A user with this email already exists.'}, status=400)

                new_user = User.objects.create_user(
                    email=email,
                    username=email.split('@')[0],
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    is_approved=True
                )
                return JsonResponse({'message': 'User created successfully', 'id': new_user.id}, status=201)

            target_user = User.objects.get(pk=body.get('user_id'))

            if action == 'update_profile':
                target_user.first_name = body.get('first_name', target_user.first_name).strip()
                target_user.last_name = body.get('last_name', target_user.last_name).strip()
                target_user.email = body.get('email', target_user.email).strip().lower()
                target_user.save()
                return JsonResponse({'message': 'User profile updated'})

            if action == 'approve':
                target_user.is_approved = True
                send_portal_notification(
                    recipient=target_user,
                    title="Account Approved!",
                    message="Your EastWest Portal account has been approved. Welcome!",
                    notification_type="system",
                    link="/core/dashboard/"
                )
            elif action == 'reject':
                target_user.is_approved = False
            elif action == 'make_faculty':
                target_user.role = 'faculty'
                target_user.is_approved = True
                send_portal_notification(
                    recipient=target_user,
                    title="Account Status Updated",
                    message="Your account has been updated to Faculty status.",
                    notification_type="system",
                    link="/core/dashboard/"
                )
            elif action == 'make_student':
                target_user.role = 'student'

            
            target_user.save()
            return JsonResponse({'message': 'User status updated'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'DELETE':
        if not user_id:
            return JsonResponse({'error': 'ID required'}, status=400)
        try:
            target_user = User.objects.get(pk=user_id)
            if target_user.is_superuser:
                return JsonResponse({'error': 'Cannot delete superuser'}, status=403)
            target_user.delete()
            return JsonResponse({'message': 'User deleted'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


@login_required
def global_search_api(request):
    """Universal search across users, posts, materials, and marketplace."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    results = []

    # 1. Search People (Approved only)
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
    ).filter(is_approved=True)[:5]
    for u in users:
        results.append({
            'type': 'People',
            'title': u.get_full_name() or u.email,
            'subtitle': u.get_role_display(),
            'url': f'#user-{u.id}', 
            'icon': 'fa-user'
        })

    # 2. Search Materials
    mats = Material.objects.filter(
        Q(title__icontains=query) | Q(course__name__icontains=query) | Q(course__code__icontains=query)
    ).filter(is_approved=True).select_related('course')[:5]
    for m in mats:
        results.append({
            'type': 'Academic',
            'title': m.title,
            'subtitle': f'{m.course.code} Material',
            'url': '/materials/',
            'icon': 'fa-book-open'
        })

    return JsonResponse({'results': results})


@login_required
@user_passes_test(is_staff)
def moderation_dashboard(request):
    """Dedicated admin page for approving/rejecting user-contributed content."""
    pending_posts = Post.objects.filter(is_approved=False).select_related('uploaded_by')
    pending_materials = Material.objects.filter(is_approved=False).select_related('uploaded_by', 'course', 'faculty').prefetch_related('attachments')

    pending_listings = Listing.objects.filter(is_approved=False).select_related('uploaded_by')
    pending_papers = Paper.objects.filter(is_approved=False).select_related('uploaded_by')
    pending_capstones = Capstone.objects.filter(is_approved=False).select_related('uploaded_by')

    from materials.models import Course
    from core.models import Enrollment, Announcement
    courses_with_enrollments = Course.objects.prefetch_related('enrolled_students__student').all()
    global_announcements = Announcement.objects.all().order_by('-created_at')


    context = {
        'pending_posts': pending_posts,
        'pending_materials': pending_materials,
        'pending_listings': pending_listings,
        'pending_papers': pending_papers,
        'pending_capstones': pending_capstones,
        'courses_with_enrollments': courses_with_enrollments,
        'global_announcements': global_announcements,
        'total_enrollments': Enrollment.objects.count(),
        'total_pending': (pending_posts.count() + pending_materials.count() + 
                         pending_listings.count() + pending_papers.count() + 
                         pending_capstones.count())
    }


    return render(request, 'core/moderation.html', context)


@login_required
@user_passes_test(is_staff)
def approve_item(request, model_name, obj_id):
    """Generic approval view."""
    try:
        model = apps.get_model(app_label=model_name.split('.')[0] if '.' in model_name else model_name, 
                             model_name=model_name.split('.')[-1] if '.' in model_name else model_name)
        obj = model.objects.get(pk=obj_id)
        obj.is_approved = True
        obj.save()
        
        # Notify uploader
        uploader = getattr(obj, 'uploaded_by', None)
        if uploader:
            title = f"{model_name.capitalize().replace('core.', '')} Approved!"
            message = f"Your item '{obj}' has been approved by an administrator."
            send_portal_notification(recipient=uploader, title=title, message=message, notification_type='system')
            
        messages.success(request, f"Approved: {obj}")
    except Exception as e:
        messages.error(request, f"Error approving item: {str(e)}")
    return redirect('core:moderation_dashboard')


@login_required
@user_passes_test(is_staff)
def reject_item(request, model_name, obj_id):
    """Generic rejection (deletion) view."""
    try:
        model = apps.get_model(app_label=model_name.split('.')[0] if '.' in model_name else model_name, 
                             model_name=model_name.split('.')[-1] if '.' in model_name else model_name)
        obj = model.objects.get(pk=obj_id)
        
        # Notify uploader before deletion
        uploader = getattr(obj, 'uploaded_by', None)
        if uploader:
            title = f"{model_name.capitalize().replace('core.', '')} Rejected"
            message = f"Your item '{obj}' was rejected and removed by an administrator."
            send_portal_notification(recipient=uploader, title=title, message=message, notification_type='system')
            
        obj.delete()
        messages.warning(request, "Item has been rejected and removed.")
    except Exception as e:
        messages.error(request, f"Error rejecting item: {str(e)}")
    return redirect('core:moderation_dashboard')



def pending_approval(request):
    """Shown to users who have registered but are awaiting admin approval."""
    if not request.user.is_authenticated:
        return redirect('account_login')
    if request.user.is_approved or request.user.is_superuser:
        return redirect('core:home')
        
    if request.method == 'POST':
        user = request.user
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        if 'id_card_image' in request.FILES:
            user.id_card_image = request.FILES['id_card_image']
        whatsapp = request.POST.get('whatsapp_number')
        if whatsapp:
            user.whatsapp_number = whatsapp
        user.save()
        messages.success(request, "Verification details submitted successfully. Admin review is pending.")
        return redirect('core:pending_approval')
        
    return render(request, 'core/pending.html')


@login_required
def enrollment_view(request):
    """View for students to select their courses for the current semester."""
    from materials.models import Course
    from .models import Enrollment
    from django.utils import timezone
    
    # Current logical semester (hardcoded for now or derived from date)
    current_year = timezone.now().year
    month = timezone.now().month
    if month <= 4: current_semester = 'Spring'
    elif month <= 8: current_semester = 'Summer'
    else: current_semester = 'Fall'

    if request.method == 'POST':
        course_ids = request.POST.getlist('courses')
        # Remove old enrollments for this specific semester/year to avoid duplicates
        Enrollment.objects.filter(student=request.user, semester=current_semester, year=current_year).delete()
        
        enrollments = [
            Enrollment(student=request.user, course_id=cid, semester=current_semester, year=current_year)
            for cid in course_ids
        ]
        Enrollment.objects.bulk_create(enrollments)
        messages.success(request, f"Enrollment for {current_semester} {current_year} updated successfully!")
        return redirect('feed:index')


    courses = Course.objects.all()
    user_enrollments = Enrollment.objects.filter(student=request.user, semester=current_semester, year=current_year).values_list('course_id', flat=True)
    
    context = {
        'courses': courses,
        'user_enrollments': list(user_enrollments),
        'current_semester': current_semester,
        'current_year': current_year,
    }
    return render(request, 'core/enrollment.html', context)


@login_required
@user_passes_test(is_staff)

def api_create_announcement(request):
    """API for admins to create new global announcements."""
    from .models import Announcement
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            category = request.POST.get('category', 'general')
            
            if not title or not content:
                messages.error(request, "Title and content are required.")
                return redirect('core:moderation_dashboard')

            Announcement.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user
            )
            messages.success(request, "Announcement published and notifications sent!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('core:moderation_dashboard')


def logout_view(request):

    from django.contrib.auth import logout
    logout(request)
    return redirect('account_login')


@login_required
def api_notifications(request):
    """Fetch unread notifications for the user."""
    from .models import Notification
    
    base_notifs = Notification.objects.filter(recipient=request.user)
    unread_count = base_notifs.filter(is_read=False).count()
    notifications = base_notifs.order_by('-created_at')[:20]

    
    notif_list = []
    for n in notifications:
        notif_list.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'link': n.link or '#',
            'created_at': n.created_at.strftime("%b %d, %I:%M %p")
        })
        
    return JsonResponse({
        'notifications': notif_list,
        'unread_count': unread_count
    })


@login_required
@csrf_exempt
def api_notifications_read(request):
    """Mark all notifications as read."""
    from .models import Notification
    
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid method'}, status=400)


@login_required
def my_uploads(request):
    """View to show user's submission history across all modules."""
    from feed.models import Post
    from materials.models import Material
    from marketplace.models import Listing

    context = {
        'posts': Post.objects.filter(uploaded_by=request.user).order_by('-created_at'),
        'materials': Material.objects.filter(uploaded_by=request.user).order_by('-created_at'),
        'listings': Listing.objects.filter(uploaded_by=request.user).order_by('-created_at'),
        'papers': Paper.objects.filter(uploaded_by=request.user).order_by('-created_at'),
        'capstones': Capstone.objects.filter(uploaded_by=request.user).order_by('-created_at'),
    }
    return render(request, 'core/my_uploads.html', context)


