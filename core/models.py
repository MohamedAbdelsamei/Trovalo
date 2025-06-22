from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)



class MissingPersonReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('found', 'Found'),
        ('deleted', 'Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=255)
    description = models.TextField()
    age = models.PositiveIntegerField()
    last_seen_location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='reports/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["last_seen_location", "age", "created_at"]),
        ]

class ModerationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.OneToOneField(MissingPersonReport, on_delete=models.CASCADE, related_name='moderation_log')
    action = models.CharField(max_length=50)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderated_reports')
    timestamp = models.DateTimeField(auto_now_add=True)