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


class Paper(models.Model):
    research_area = models.ForeignKey(ResearchArea, on_delete=models.CASCADE, related_name='papers')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    authors = models.CharField(max_length=400)
    abstract = models.TextField(blank=True)
    publication_year = models.PositiveIntegerField()
    pdf_link = models.URLField(max_length=1000, blank=True)
    citations = models.PositiveIntegerField(default=0)
    dataset_link = models.URLField(max_length=1000, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publication_year', '-citations']

    def __str__(self):
        return self.title


CAPSTONE_STATUS_CHOICES = [
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('archived', 'Archived'),
]


class Capstone(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_title = models.CharField(max_length=400)
    batch_year = models.PositiveIntegerField()
    faculty_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='supervised_capstones')
    team_members = models.TextField(help_text='Comma-separated list of team members')
    project_description = models.TextField(blank=True)
    report_pdf = models.URLField(max_length=1000, blank=True)
    presentation_slides = models.URLField(max_length=1000, blank=True)
    demo_video = models.URLField(max_length=1000, blank=True)
    gallery_images = models.TextField(blank=True, help_text='Comma-separated image URLs')
    status = models.CharField(max_length=20, choices=CAPSTONE_STATUS_CHOICES, default='ongoing')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-batch_year', 'project_title']

    def __str__(self):
        return f"[{self.batch_year}] {self.project_title}"
