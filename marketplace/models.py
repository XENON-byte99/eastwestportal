from django.db import models
from django.conf import settings


LISTING_TYPE_CHOICES = [
    ('sell', 'Sell'),
    ('buy', 'Buy'),
    ('exchange', 'Exchange'),
]

CONDITION_CHOICES = [
    ('like-new', 'Like New'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('needs-repair', 'Needs Repair'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('sold', 'Sold'),
    ('removed', 'Removed'),
]


class Listing(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    seller_name = models.CharField(max_length=150)
    seller_contact = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='sell')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='marketplace/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item_name} ({self.listing_type}) — {self.seller_name}"


class ChatMessage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
