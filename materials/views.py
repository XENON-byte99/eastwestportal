import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Material, Course, MaterialType, MaterialAttachment, MaterialRating



User = get_user_model()


def is_staff(user):
    return user.is_staff or user.is_superuser or user.role == 'admin'


@login_required
def index(request):
    return render(request, 'materials/materials.html')


@login_required
@user_passes_test(is_staff)
def manage_courses(request):
    """View to render the Course Management page."""
    return render(request, 'materials/manage_courses.html')


@login_required
@user_passes_test(is_staff)
def manage_material_types(request):
    """View to render the Material Type Management page."""
    return render(request, 'materials/manage_types.html')


@login_required
@require_http_methods(['GET', 'POST', 'PATCH', 'DELETE'])
@user_passes_test(is_staff)
def api_course_manage(request, course_id=None):
    """CRUD API for Courses (Admin only)."""
    if request.method == 'GET':
        courses = list(Course.objects.all().values('id', 'code', 'name', 'credits', 'department', 'created_at'))
        return JsonResponse({'courses': courses})

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            code = body.get('code', '').strip().upper()
            name = body.get('name', '').strip()
            credits = body.get('credits', '').strip()
            dept = body.get('department', '').strip()

            if not code or not name:
                return JsonResponse({'error': 'Code and Name are required.'}, status=400)

            if Course.objects.filter(code=code).exists():
                return JsonResponse({'error': f'Course with code {code} already exists.'}, status=400)

            course = Course.objects.create(code=code, name=name, credits=credits, department=dept)
            return JsonResponse({'id': course.id, 'message': 'Course created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'PATCH':
        if not course_id:
            return JsonResponse({'error': 'ID required for update.'}, status=400)
        try:
            body = json.loads(request.body)
            course = Course.objects.get(pk=course_id)
            if 'code' in body:
                course.code = body['code'].strip().upper()
            if 'name' in body:
                course.name = body['name'].strip()
            if 'credits' in body:
                course.credits = body['credits'].strip()
            if 'department' in body:
                course.department = body['department'].strip()
            course.save()
            return JsonResponse({'message': 'Course updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'DELETE':
        if not course_id:
            return JsonResponse({'error': 'ID required for deletion.'}, status=400)
        try:
            course = Course.objects.get(pk=course_id)
            course.delete()
            return JsonResponse({'message': 'Course deleted successfully'})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found.'}, status=404)


@login_required
@require_http_methods(['GET', 'POST', 'PATCH', 'DELETE'])
@user_passes_test(is_staff)
def api_material_type_manage(request, type_id=None):
    """CRUD API for Material Types (Admin only)."""
    if request.method == 'GET':
        types = list(MaterialType.objects.all().values('id', 'name', 'icon', 'created_at'))
        return JsonResponse({'types': types})

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            name = body.get('name', '').strip()
            icon = body.get('icon', 'fa-file').strip()

            if not name:
                return JsonResponse({'error': 'Name is required.'}, status=400)

            if MaterialType.objects.filter(name=name).exists():
                return JsonResponse({'error': f'Type "{name}" already exists.'}, status=400)

            mtype = MaterialType.objects.create(name=name, icon=icon)
            return JsonResponse({'id': mtype.id, 'message': 'Type created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'PATCH':
        if not type_id:
            return JsonResponse({'error': 'ID required for update.'}, status=400)
        try:
            body = json.loads(request.body)
            mtype = MaterialType.objects.get(pk=type_id)
            if 'name' in body:
                mtype.name = body['name'].strip()
            if 'icon' in body:
                mtype.icon = body['icon'].strip()
            mtype.save()
            return JsonResponse({'message': 'Category updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'DELETE':
        if not type_id:
            return JsonResponse({'error': 'ID required.'}, status=400)
        try:
            mtype = MaterialType.objects.get(pk=type_id)
            mtype.delete()
            return JsonResponse({'message': 'Type deleted successfully'})
        except MaterialType.DoesNotExist:
            return JsonResponse({'error': 'Not found.'}, status=404)


@login_required
@require_http_methods(['GET', 'POST'])
def api_materials(request):
    if request.method == 'GET':
        qs = Material.objects.select_related('course', 'faculty', 'uploaded_by', 'material_type').all()
        
        # Regular users only see approved materials
        # Regular users only see approved materials OR their own uploads
        if not request.user.is_portal_admin:
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))

            
        course_id = request.GET.get('course_id')
        faculty_id = request.GET.get('faculty_id')
        type_id = request.GET.get('type_id')
        enrolled_only = request.GET.get('enrolled_only') == 'true'
        
        if enrolled_only:
            from core.models import Enrollment
            from django.utils import timezone
            now = timezone.now()
            month = now.month
            if month <= 4: sem = 'Spring'
            elif month <= 8: sem = 'Summer'
            else: sem = 'Fall'
            
            # Get course IDs user is enrolled in for current semester/year
            enrolled_course_ids = Enrollment.objects.filter(
                student=request.user, 
                semester=sem, 
                year=now.year
            ).values_list('course_id', flat=True)
            qs = qs.filter(course_id__in=enrolled_course_ids)

        if course_id:
            qs = qs.filter(course_id=course_id)
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        if type_id:
            qs = qs.filter(material_type_id=type_id)

        # Get current user's ratings for these materials
        user_ratings = {}
        if request.user.is_authenticated:
            user_ratings = {r.material_id: r.score for r in MaterialRating.objects.filter(user=request.user, material__in=qs)}

        data = [{
            'id': m.id,
            'course_id': m.course.id,
            'course_code': m.course.code,
            'course_name': m.course.name,
            'faculty_id': m.faculty.id,
            'faculty_name': m.faculty.get_full_name() or m.faculty.email,
            'type_id': m.material_type.id,
            'type_name': m.material_type.name,
            'type_icon': m.material_type.icon,
            'title': m.title,
            'description': m.description,
            'attachments': [
                {
                    'id': a.id,
                    'name': a.name,
                    'is_link': a.is_link,
                    'url': a.link_url if a.is_link else (a.file.url if a.file else None)
                } for a in m.attachments.all()
            ],
            'semester': m.semester,

            'year': m.year,
            'order': m.order,
            'is_approved': m.is_approved,
            'average_rating': round(m.average_rating, 1),
            'rating_count': m.rating_count,
            'uploaded_by': m.uploaded_by.get_full_name() or m.uploaded_by.email,
            'user_rating': user_ratings.get(m.id, 0),
            'can_edit': (m.uploaded_by == request.user or request.user.is_portal_admin),

        } for m in qs]
        return JsonResponse({'materials': data})


    # POST - Create new material
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            course_id = body.get('course_id')
            faculty_id = body.get('faculty_id')
            type_id = body.get('type_id')
            title = body.get('title', '')
            description = body.get('description', '')
            url = body.get('url', '')
            order = body.get('order', 1)
        else:
            course_id = request.POST.get('course_id')
            faculty_id = request.POST.get('faculty_id')
            type_id = request.POST.get('type_id')
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            order = request.POST.get('order', 1)
            semester = request.POST.get('semester', '')

            year = request.POST.get('year')
            if year == '': year = None

    except Exception:
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    # Validate IDs
    try:
        course = Course.objects.get(pk=course_id)
        faculty = User.objects.get(pk=faculty_id, role='faculty')
        mtype = MaterialType.objects.get(pk=type_id)
    except (Course.DoesNotExist, User.DoesNotExist, MaterialType.DoesNotExist):
        return JsonResponse({'error': 'Selected data was not found.'}, status=400)

    is_approved = True if request.user.role == 'faculty' or request.user.is_portal_admin else False

    m = Material.objects.create(
        uploaded_by=request.user,
        course=course,
        faculty=faculty,
        material_type=mtype,
        title=title,
        description=description,
        semester=semester,
        year=year,
        order=order,
        is_approved=is_approved
    )

    # Trigger Notifications
    from core.models import Notification
    if not is_approved:
        # Notify staff about new submission
        staff_users = User.objects.filter(Q(is_staff=True) | Q(role='admin'))
        for staff in staff_users:
            Notification.objects.create(
                recipient=staff,
                sender=request.user,
                notification_type='new_material',
                title='New Material Submission',
                message=f'{request.user.get_full_name()} submitted "{title}" for review.',
                link='/core/moderation/'

            )


    
    # Handle files
    for f in request.FILES.getlist('files'):
        MaterialAttachment.objects.create(
            material=m,
            file=f,
            is_link=False,
            name=f.name
        )

    # Handle links
    for link in request.POST.getlist('links'):
        if link.strip():
            MaterialAttachment.objects.create(
                material=m,
                link_url=link.strip(),
                is_link=True,
                name='External Link'
            )

    message = 'Material uploaded!' if is_approved else 'Material submitted for admin review.'

    return JsonResponse({'id': m.id, 'message': message, 'is_approved': is_approved}, status=201)


@login_required
@require_http_methods(['GET', 'POST', 'PATCH', 'DELETE'])

def api_material_detail(request, material_id):
    try:
        m = Material.objects.select_related('course', 'faculty', 'material_type').get(pk=material_id)
    except Material.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': m.id, 
            'course_code': m.course.code,
            'faculty_name': m.faculty.get_full_name() or m.faculty.email,
            'type_name': m.material_type.name, 
            'title': m.title,
            'description': m.description, 
            'attachments': [
                {
                    'id': a.id,
                    'name': a.name,
                    'is_link': a.is_link,
                    'url': a.link_url if a.is_link else (a.file.url if a.file else None)
                } for a in m.attachments.all()
            ],
            'semester': m.semester,

            'year': m.year,
            'uploaded_by': m.uploaded_by.email,
            'is_approved': m.is_approved

        })
    
    if request.method in ['POST', 'PATCH']:
        if m.uploaded_by == request.user or request.user.is_portal_admin:
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body)
                else:
                    body = request.POST

                if 'title' in body: m.title = body['title']
                if 'description' in body: m.description = body['description']
                if 'order' in body: m.order = body['order']
                if 'semester' in body: m.semester = body['semester']
                if 'year' in body: m.year = body['year'] if body['year'] != '' else None

                
                # Allow staff to approve
                if 'is_approved' in body and request.user.is_portal_admin:
                    old_status = m.is_approved
                    # Handle both boolean and string "true"/"false"
                    val = body['is_approved']
                    if isinstance(val, str):
                        m.is_approved = val.lower() == 'true'
                    else:
                        m.is_approved = bool(val)
                    
                    # Notify uploader if approved
                    if m.is_approved and not old_status:
                        from core.models import Notification
                        Notification.objects.create(
                            recipient=m.uploaded_by,
                            sender=request.user,
                            notification_type='material_approval',
                            title='Material Approved!',
                            message=f'Your resource "{m.title}" has been approved and is now live.',
                            link='/materials/'
                        )
                
                # Handle appending files

                if request.FILES:
                    for f in request.FILES.getlist('files'):
                        MaterialAttachment.objects.create(
                            material=m,
                            file=f,
                            is_link=False,
                            name=f.name
                        )

                # Handle appending links
                if request.POST:
                    for link in request.POST.getlist('links'):
                        if link.strip():
                            MaterialAttachment.objects.create(
                                material=m,
                                link_url=link.strip(),
                                is_link=True,
                                name='External Link'
                            )
                
                m.save()

                return JsonResponse({'message': 'Material updated successfully', 'is_approved': m.is_approved})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'DELETE':
        if m.uploaded_by == request.user or request.user.is_portal_admin:
            m.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)



@login_required
def api_courses(request):
    """
    Return all available courses, faculty members, and material types for UI population.
    """
    courses = list(Course.objects.values('id', 'code', 'name', 'credits', 'department'))
    faculty = list(User.objects.filter(role='faculty').values('id', 'first_name', 'last_name', 'email'))
    m_types = list(MaterialType.objects.values('id', 'name', 'icon'))
    
    for f in faculty:
        name = f"{f['first_name']} {f['last_name']}".strip()
        f['full_name'] = name if name else f['email']
        
    return JsonResponse({
        'courses': courses,
        'faculty': faculty,
        'types': m_types
    })


@login_required
@require_http_methods(['POST'])
def api_rate_material(request, material_id):
    try:
        m = Material.objects.get(pk=material_id)
        body = json.loads(request.body)
        score = int(body.get('score'))
        if not (1 <= score <= 5):
            return JsonResponse({'error': 'Invalid score'}, status=400)
            
        rating, created = MaterialRating.objects.update_or_create(
            material=m, user=request.user,
            defaults={'score': score}
        )
        # Re-fetch to get updated averages
        m.refresh_from_db()
        return JsonResponse({
            'message': 'Rating submitted!',
            'average_rating': round(m.average_rating, 1),
            'rating_count': m.rating_count
        })
    except (Material.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

@login_required
@require_http_methods(['DELETE'])
def api_attachment_delete(request, attachment_id):
    try:
        attachment = MaterialAttachment.objects.get(pk=attachment_id)
        if attachment.material.uploaded_by == request.user or request.user.is_portal_admin:
            attachment.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    except MaterialAttachment.DoesNotExist:
        return JsonResponse({'error': 'Attachment not found'}, status=404)

