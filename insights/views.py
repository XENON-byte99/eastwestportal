from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Insight
from materials.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def index(request):
    # Faculty members are not allowed to see insights (as per user request)
    if request.user.is_faculty and not request.user.is_portal_admin:
        return HttpResponseForbidden("Faculty members do not have access to insights.")
    
    insights = Insight.objects.all().select_related('course', 'faculty', 'author')
    courses = Course.objects.all()
    faculties = User.objects.filter(role='faculty')
    
    return render(request, 'insights/list.html', {
        'insights': insights,
        'courses': courses,
        'faculties': faculties,
    })

@login_required
def create_insight(request):
    if not request.user.is_portal_admin:
        return HttpResponseForbidden("Only admins can create insights.")
    
    if request.method == 'POST':
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
    
    return redirect('insights:index')

@login_required
def delete_insight(request, pk):
    if not request.user.is_portal_admin:
        return HttpResponseForbidden("Only admins can delete insights.")
    
    insight = get_object_or_404(Insight, pk=pk)
    insight.delete()
    messages.success(request, "Insight deleted successfully!")
    return redirect('insights:index')
