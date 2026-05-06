from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user with approval workflow and role."""

    ROLE_STUDENT = 'student'
    ROLE_FACULTY = 'faculty'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_FACULTY, 'Faculty'),
        (ROLE_ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    is_approved = models.BooleanField(
        default=False,
        help_text='Must be approved by admin before gaining portal access.'
    )
    student_id = models.CharField(max_length=30, blank=True, help_text='Optional student/faculty ID number')
    department = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    id_card_image = models.ImageField(upload_to='id_cards/', null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text='WhatsApp number for verification')
    bio = models.TextField(max_length=300, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_portal_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_faculty(self):
        return self.role == self.ROLE_FACULTY

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('material_approval', 'Material Approval'),
        ('new_material', 'New Material Submission'),
        ('announcement', 'General Announcement'),
        ('system', 'System Message'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, help_text="Relative URL to redirect on click")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('urgent', 'Urgent'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Create notifications for all active users
            from django.contrib.auth import get_user_model
            from core.utils import bulk_send_notifications
            User = get_user_model()
            users = User.objects.filter(is_active=True)
            
            bulk_send_notifications(
                recipients=users,
                title=f'New Announcement: {self.title}',
                message=self.content[:100] + '...',
                notification_type='announcement',
                link='/core/notices/',
                sender=self.author
            )


class Enrollment(models.Model):
    SEMESTER_CHOICES = [
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('materials.Course', on_delete=models.CASCADE, related_name='enrolled_students')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'semester', 'year')
        ordering = ['-year', 'semester', 'course__code']

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.code} ({self.semester} {self.year})"
