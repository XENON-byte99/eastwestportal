from django.db import models
from django.conf import settings


class ResearchArea(models.Model):
    research_area = models.CharField(max_length=300)
    lead_faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='research_leads')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🔬')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['research_area']

    def __str__(self):
        return self.research_area


SEMESTER_CHOICES = [
    ('Spring', 'Spring'),
    ('Summer', 'Summer'),
    ('Fall', 'Fall'),
]


class Paper(models.Model):
    research_area = models.ForeignKey(ResearchArea, on_delete=models.CASCADE, related_name='papers', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    field = models.CharField(max_length=200, blank=True, help_text="Specific field of research")
    faculty_name = models.CharField(max_length=200, blank=True, help_text="Name of faculty supervisor/advisor")
    authors = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    passing_year = models.PositiveIntegerField(default=2024)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='Spring')
    pdf_file = models.FileField(upload_to='research/papers/', null=True, blank=True)
    pdf_link = models.URLField(max_length=1000, blank=True)
    citations = models.PositiveIntegerField(default=0)
    dataset_link = models.URLField(max_length=1000, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-passing_year', '-citations']

    def __str__(self):
        return self.title


CAPSTONE_STATUS_CHOICES = [
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('archived', 'Archived'),
]


class Capstone(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    field = models.CharField(max_length=200, blank=True, help_text="Project category/field")
    faculty_name = models.CharField(max_length=200, blank=True, help_text="Name of faculty supervisor")
    passing_year = models.PositiveIntegerField(default=2024)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='Spring')
    team_members = models.TextField(help_text='Comma-separated list of team members')
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='research/capstones/', null=True, blank=True)
    pdf_link = models.URLField(max_length=1000, blank=True)
    presentation_slides = models.URLField(max_length=1000, blank=True)
    demo_video = models.URLField(max_length=1000, blank=True)
    gallery_images = models.TextField(blank=True, help_text='Comma-separated image URLs')
    status = models.CharField(max_length=20, choices=CAPSTONE_STATUS_CHOICES, default='ongoing')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-passing_year', 'title']

    def __str__(self):
        return f"[{self.passing_year}] {self.title}"
