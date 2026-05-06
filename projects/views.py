import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ResearchArea, Paper, Capstone


@login_required
def index(request):
    areas = ResearchArea.objects.all()
    return render(request, 'projects/projects.html', {'areas': areas})


# ── Research Areas ──

@login_required

@require_http_methods(['GET', 'POST'])
def api_research_areas(request):
    if request.method == 'GET':
        areas = ResearchArea.objects.all()
        data = [{
            'id': a.id,
            'research_area': a.research_area,
            'lead_faculty': a.lead_faculty.get_full_name() or a.lead_faculty.email,
            'description': a.description,
            'icon': a.icon,
            'paper_count': a.papers.filter(is_approved=True).count(),
        } for a in areas]
        return JsonResponse({'areas': data})

    # Only staff/admin can create research areas
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    area = ResearchArea.objects.create(
        research_area=body.get('research_area', ''),
        lead_faculty_id=body.get('lead_faculty_id', request.user.id),
        description=body.get('description', ''),
        icon=body.get('icon', '🔬'),
    )
    return JsonResponse({'id': area.id}, status=201)


# ── Papers ──

@login_required

@require_http_methods(['GET', 'POST'])
def api_papers(request):
    if request.method == 'GET':
        area_id = request.GET.get('area_id')
        search = request.GET.get('search')
        field = request.GET.get('field')
        faculty = request.GET.get('faculty')
        year = request.GET.get('year')
        semester = request.GET.get('semester')

        qs = Paper.objects.select_related('research_area', 'uploaded_by').all()
        
        if not request.user.is_staff:
            from django.db.models import Q
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))

        if area_id:
            qs = qs.filter(research_area_id=area_id)
        
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(field__icontains=search) |
                Q(faculty_name__icontains=search) |
                Q(authors__icontains=search) |
                Q(description__icontains=search)
            )
        
        if field:
            qs = qs.filter(field__icontains=field)
        if faculty:
            qs = qs.filter(faculty_name__icontains=faculty)
        if year:
            qs = qs.filter(passing_year=year)
        if semester:
            qs = qs.filter(semester=semester)
            
        data = [{
            'id': p.id,
            'research_area_id': p.research_area_id,
            'title': p.title,
            'field': p.field,
            'faculty_name': p.faculty_name,
            'authors': p.authors,
            'description': p.description,
            'passing_year': p.passing_year,
            'semester': p.semester,
            'pdf_file': p.pdf_file.url if p.pdf_file else None,
            'pdf_link': p.pdf_link,
            'citations': p.citations,
            'dataset_link': p.dataset_link,
            'uploaded_by': p.uploaded_by.get_full_name() or p.uploaded_by.email,
        } for p in qs]
        return JsonResponse({'papers': data})

    # POST - Submit Paper
    try:
        # Support both JSON and multipart form data (for files)
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            area_id = body.get('research_area_id')
            title = body.get('title', '')
            field = body.get('field', '')
            faculty_name = body.get('faculty_name', '')
            authors = body.get('authors', '')
            description = body.get('description', '')
            passing_year = body.get('passing_year', 2024)
            semester = body.get('semester', 'Spring')
            pdf_link = body.get('pdf_link', '')
        else:
            area_id = request.POST.get('research_area_id')
            title = request.POST.get('title', '')
            field = request.POST.get('field', '')
            faculty_name = request.POST.get('faculty_name', '')
            authors = request.POST.get('authors', '')
            description = request.POST.get('description', '')
            passing_year = request.POST.get('passing_year', 2024)
            semester = request.POST.get('semester', 'Spring')
            pdf_link = request.POST.get('pdf_link', '')

        pdf_file = request.FILES.get('pdf_file')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Faculty members are automatically approved
    is_approved = True if request.user.role == 'faculty' or request.user.is_staff else False

    paper = Paper.objects.create(
        research_area_id=area_id if area_id else None,
        uploaded_by=request.user,
        title=title,
        field=field,
        faculty_name=faculty_name,
        authors=authors,
        description=description,
        passing_year=passing_year,
        semester=semester,
        pdf_file=pdf_file,
        pdf_link=pdf_link,
        is_approved=is_approved
    )
    
    if not is_approved:
        from core.utils import notify_admins
        notify_admins(
            title="New Research Paper Awaiting Review",
            message=f"{request.user.get_full_name() or request.user.email} submitted a paper '{title}' that requires approval.",
            notification_type="system",
            link="/core/moderation/"
        )

    message = 'Paper published!' if is_approved else 'Paper submitted for admin review.'
    return JsonResponse({'id': paper.id, 'message': message, 'is_approved': is_approved}, status=201)


# ── Capstones ──

@login_required

@require_http_methods(['GET', 'POST'])
def api_capstones(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        field = request.GET.get('field')
        faculty = request.GET.get('faculty')
        year = request.GET.get('year')
        semester = request.GET.get('semester')
        batch = request.GET.get('batch') or year # backward compatibility

        qs = Capstone.objects.select_related('uploaded_by').all()
        
        if not request.user.is_staff:
            from django.db.models import Q
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))
            
        if batch:
            qs = qs.filter(passing_year=batch)

        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(field__icontains=search) |
                Q(faculty_name__icontains=search) |
                Q(team_members__icontains=search) |
                Q(description__icontains=search)
            )
        
        if field:
            qs = qs.filter(field__icontains=field)
        if faculty:
            qs = qs.filter(faculty_name__icontains=faculty)
        if semester:
            qs = qs.filter(semester=semester)

        data = [{
            'id': c.id,
            'title': c.title,
            'field': c.field,
            'faculty_name': c.faculty_name,
            'passing_year': c.passing_year,
            'semester': c.semester,
            'team_members': c.team_members,
            'description': c.description,
            'pdf_file': c.pdf_file.url if c.pdf_file else None,
            'pdf_link': c.pdf_link,
            'presentation_slides': c.presentation_slides,
            'status': c.get_status_display(),
            'uploaded_by': c.uploaded_by.get_full_name() or c.uploaded_by.email,
        } for c in qs]
        return JsonResponse({'capstones': data})

    # POST - Submit Capstone
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            title = body.get('title', '')
            field = body.get('field', '')
            faculty_name = body.get('faculty_name', '')
            passing_year = body.get('passing_year', 2024)
            semester = body.get('semester', 'Spring')
            team_members = body.get('team_members', '')
            description = body.get('description', '')
            pdf_link = body.get('pdf_link', '')
        else:
            title = request.POST.get('title', '')
            field = request.POST.get('field', '')
            faculty_name = request.POST.get('faculty_name', '')
            passing_year = request.POST.get('passing_year', 2024)
            semester = request.POST.get('semester', 'Spring')
            team_members = request.POST.get('team_members', '')
            description = request.POST.get('description', '')
            pdf_link = request.POST.get('pdf_link', '')
        
        pdf_file = request.FILES.get('pdf_file')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Faculty members are automatically approved
    is_approved = True if request.user.role == 'faculty' or request.user.is_staff else False

    capstone = Capstone.objects.create(
        uploaded_by=request.user,
        title=title,
        field=field,
        faculty_name=faculty_name,
        passing_year=passing_year,
        semester=semester,
        team_members=team_members,
        description=description,
        pdf_file=pdf_file,
        pdf_link=pdf_link,
        status='ongoing',
        is_approved=is_approved
    )
    
    if not is_approved:
        from core.utils import notify_admins
        notify_admins(
            title="New Capstone Project Awaiting Review",
            message=f"{request.user.get_full_name() or request.user.email} submitted a capstone '{title}' that requires approval.",
            notification_type="system",
            link="/core/moderation/"
        )

    message = 'Capstone project published!' if is_approved else 'Capstone submitted for admin review.'
    return JsonResponse({'id': capstone.id, 'message': message, 'is_approved': is_approved}, status=201)

@login_required

@require_http_methods(['PATCH', 'DELETE'])
def api_paper_detail(request, paper_id):
    try:
        paper = Paper.objects.get(pk=paper_id)
    except Paper.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'PATCH':
        if paper.uploaded_by == request.user or request.user.is_staff or request.user.role == 'admin':
            try:
                body = json.loads(request.body)
                for field in ['title', 'field', 'faculty_name', 'authors', 'description', 'passing_year', 'semester', 'pdf_link']:
                    if field in body:
                        setattr(paper, field, body[field])
                paper.save()
                return JsonResponse({'status': 'updated'})
            except Exception:
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'DELETE':
        if paper.uploaded_by == request.user or request.user.is_staff or request.user.role == 'admin':
            paper.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)



@login_required

@require_http_methods(['PATCH', 'DELETE'])
def api_capstone_detail(request, capstone_id):
    try:
        capstone = Capstone.objects.get(pk=capstone_id)
    except Capstone.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'PATCH':
        if capstone.uploaded_by == request.user or request.user.is_staff:
            try:
                body = json.loads(request.body)
                for field in ['status', 'title', 'field', 'faculty_name', 'description', 'passing_year', 'semester', 'pdf_link']:
                    if field in body:
                        setattr(capstone, field, body[field])
                capstone.save()
                return JsonResponse({'status': 'updated'})
            except Exception:
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if capstone.uploaded_by == request.user or request.user.is_staff:
        capstone.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Unauthorized'}, status=403)
