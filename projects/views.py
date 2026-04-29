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
@csrf_exempt
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
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_papers(request):
    if request.method == 'GET':
        area_id = request.GET.get('area_id')
        qs = Paper.objects.select_related('research_area', 'uploaded_by').all()
        
        if not request.user.is_staff:
            from django.db.models import Q
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))

            
        if area_id:
            qs = qs.filter(research_area_id=area_id)
            
        data = [{
            'id': p.id,
            'research_area_id': p.research_area_id,
            'title': p.title,
            'authors': p.authors,
            'abstract': p.abstract,
            'publication_year': p.publication_year,
            'pdf_link': p.pdf_link,
            'citations': p.citations,
            'dataset_link': p.dataset_link,
            'uploaded_by': p.uploaded_by.get_full_name() or p.uploaded_by.email,
        } for p in qs]
        return JsonResponse({'papers': data})

    # POST - Submit Paper
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            area_id = body.get('research_area_id')
            title = body.get('title', '')
            authors = body.get('authors', '')
            abstract = body.get('abstract', '')
            publication_year = body.get('publication_year', 2024)
            pdf_link = body.get('pdf_link', '')
        else:
            area_id = request.POST.get('research_area_id')
            title = request.POST.get('title', '')
            authors = request.POST.get('authors', '')
            abstract = request.POST.get('abstract', '')
            publication_year = request.POST.get('publication_year', 2024)
            pdf_link = request.POST.get('pdf_link', '')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Faculty members are automatically approved
    is_approved = True if request.user.role == 'faculty' or request.user.is_staff else False

    paper = Paper.objects.create(
        research_area_id=area_id,
        uploaded_by=request.user,
        title=title,
        authors=authors,
        abstract=abstract,
        publication_year=publication_year,
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
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_capstones(request):
    if request.method == 'GET':
        qs = Capstone.objects.select_related('uploaded_by').all()
        
        if not request.user.is_staff:
            from django.db.models import Q
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))

            
        batch = request.GET.get('batch')
        if batch:
            qs = qs.filter(batch_year=batch)

        data = [{
            'id': c.id,
            'project_title': c.project_title,
            'batch_year': c.batch_year,
            'faculty_supervisor': c.faculty_supervisor.get_full_name() if c.faculty_supervisor else 'N/A',
            'team_members': c.team_members,
            'project_description': c.project_description,
            'report_pdf': c.report_pdf,
            'presentation_slides': c.presentation_slides,
            'status': c.get_status_display(),
            'uploaded_by': c.uploaded_by.get_full_name() or c.uploaded_by.email,
        } for c in qs]
        return JsonResponse({'capstones': data})

    # POST - Submit Capstone
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            project_title = body.get('project_title', '')
            batch_year = body.get('batch_year', 2024)
            team_members = body.get('team_members', '')
            project_description = body.get('project_description', '')
        else:
            project_title = request.POST.get('project_title', '')
            batch_year = request.POST.get('batch_year', 2024)
            team_members = request.POST.get('team_members', '')
            project_description = request.POST.get('project_description', '')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Faculty members are automatically approved
    is_approved = True if request.user.role == 'faculty' or request.user.is_staff else False

    capstone = Capstone.objects.create(
        uploaded_by=request.user,
        project_title=project_title,
        batch_year=batch_year,
        team_members=team_members,
        project_description=project_description,
        status='ongoing',
        is_approved=is_approved
    )
    
    if not is_approved:
        from core.utils import notify_admins
        notify_admins(
            title="New Capstone Project Awaiting Review",
            message=f"{request.user.get_full_name() or request.user.email} submitted a capstone '{project_title}' that requires approval.",
            notification_type="system",
            link="/core/moderation/"
        )

    
    message = 'Capstone project published!' if is_approved else 'Capstone submitted for admin review.'
    return JsonResponse({'id': capstone.id, 'message': message, 'is_approved': is_approved}, status=201)

@login_required
@csrf_exempt
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
                for field in ['title', 'authors', 'abstract', 'pdf_link']:
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
@csrf_exempt
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
                for field in ['status', 'project_title', 'project_description']:
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
