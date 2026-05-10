from django.db import models
from django.conf import settings

class Insight(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_insights')
    course = models.ForeignKey('materials.Course', on_delete=models.CASCADE, related_name='insights')
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_insights', limit_choices_to={'role': 'faculty'})
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Insight for {self.course.code} by {self.author.username}"
