from django.db import models
from django.conf import settings

class Post(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('materials.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    content = models.TextField()

    media = models.ImageField(upload_to='feed/media/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.uploaded_by}: {self.content[:50]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.uploaded_by} on Post#{self.post_id}"
