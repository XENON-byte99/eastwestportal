import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Insight, Comment
from materials.models import Course
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@login_required
def index(request):
    if request.user.is_faculty and not request.user.is_portal_admin:
        return HttpResponseForbidden("Faculty members do not have access to insights.")
    
    # Filtering logic
    course_filter = request.GET.get('course')
    faculty_filter = request.GET.get('faculty')
    search_query = request.GET.get('q')
    
    insights = Insight.objects.all().select_related('course', 'faculty', 'author').prefetch_related('comments', 'comments__author')
    
    if course_filter:
        insights = insights.filter(course_id=course_filter)
    if faculty_filter:
        insights = insights.filter(faculty_id=faculty_filter)
    if search_query:
        insights = insights.filter(Q(content__icontains=search_query) | Q(course__code__icontains=search_query))
        
    courses = Course.objects.all()
    faculties = User.objects.filter(role='faculty')
    
    return render(request, 'insights/list.html', {
        'insights': insights,
        'courses': courses,
        'faculties': faculties,
        'selected_course': course_filter,
        'selected_faculty': faculty_filter,
        'search_query': search_query,
    })

@login_required
@require_http_methods(['POST'])
def create_insight(request):
    if not request.user.is_portal_admin:
        return HttpResponseForbidden("Only admins can create insights.")
    
    course_id = request.POST.get('course')
    faculty_id = request.POST.get('faculty')
    content = request.POST.get('content')
    
    course = get_object_or_404(Course, id=course_id)
    faculty = get_object_or_404(User, id=faculty_id, role='faculty')
    
    Insight.objects.create(
        author=request.user,
        course=course,
        faculty=faculty,
        content=content
    )
    messages.success(request, "Insight created successfully!")
    return redirect('insights:index')

@login_required
@require_http_methods(['POST'])
def update_insight(request, pk):
    if not request.user.is_portal_admin:
        return HttpResponseForbidden("Only admins can update insights.")
    
    insight = get_object_or_404(Insight, pk=pk)
    insight.content = request.POST.get('content')
    insight.course_id = request.POST.get('course')
    insight.faculty_id = request.POST.get('faculty')
    insight.save()
    
    messages.success(request, "Insight updated successfully!")
    return redirect('insights:index')

@login_required
@require_http_methods(['POST'])
def delete_insight(request, pk):
    if not request.user.is_portal_admin:
        return HttpResponseForbidden("Only admins can delete insights.")
    
    insight = get_object_or_404(Insight, pk=pk)
    insight.delete()
    messages.success(request, "Insight deleted successfully!")
    return redirect('insights:index')

# --- Comment API ---

@login_required
@require_http_methods(['POST'])
def api_add_comment(request, insight_id):
    insight = get_object_or_404(Insight, pk=insight_id)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            content = body.get('content', '')
        else:
            content = request.POST.get('content', '')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)
        
    comment = Comment.objects.create(
        insight=insight,
        author=request.user,
        content=content
    )
    
    return JsonResponse({
        'id': comment.id,
        'author': comment.author.get_full_name() or comment.author.email,
        'content': comment.content,
        'avatar_initials': f"{comment.author.first_name[0]}{comment.author.last_name[0]}" if comment.author.first_name and comment.author.last_name else "U",
        'can_edit': True,
        'can_delete': True,
        'created_at': 'Just now'
    })

@login_required
@require_http_methods(['PATCH', 'DELETE'])
def api_comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if request.method == 'PATCH':
        if comment.author != request.user and not request.user.is_portal_admin:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        try:
            body = json.loads(request.body)
            comment.content = body.get('content', comment.content)
            comment.save()
            return JsonResponse({'status': 'updated', 'content': comment.content})
        except Exception:
            return JsonResponse({'error': 'Invalid request'}, status=400)
            
    if request.method == 'DELETE':
        if comment.author == request.user or request.user.is_portal_admin:
            comment.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)
