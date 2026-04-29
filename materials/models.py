from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, help_text="e.g. CSE101")
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class MaterialType(models.Model):
    """Dynamic categories defined by Admin (e.g. Curriculum, Slides, Solutions)."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='fa-file', help_text="FontAwesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Material(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_materials')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    # Link specifically to a faculty user
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_materials', limit_choices_to={'role': 'faculty'})
    
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, related_name='materials')
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    SEMESTER_CHOICES = [

        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    ]
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    
    is_approved = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['course__code', 'faculty__last_name', 'order']

    def __str__(self):
        return f"[{self.material_type.name}] {self.title} — {self.course.code}"


class MaterialAttachment(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='materials/attachments/', null=True, blank=True)
    link_url = models.URLField(max_length=1000, blank=True)
    is_link = models.BooleanField(default=False)
    name = models.CharField(max_length=300, blank=True, help_text="Display name for the file or link")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name or (self.link_url if self.is_link else self.file.name)

