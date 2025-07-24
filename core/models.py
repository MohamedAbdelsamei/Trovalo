from django.db import models
import uuid,json
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator


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
    national_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            MinLengthValidator(8),
            MaxLengthValidator(20)
        ],
        help_text="National identification number (8-20 characters)",
        null=True,
        blank=True  # Only if national ID might be unknown
    )
    face_encoding = models.TextField(null=True, blank=True)  # Stores face vector
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
        constraints = [
            models.UniqueConstraint(
                fields=["national_id"],
                name="unique_national_id",
                condition=models.Q(national_id__isnull=False)
            ),  
        ]

    def set_face_encoding(self, encoding):    
        """Store encoding as JSON string"""   
        self.face_encoding = json.dumps(encoding)

    def get_face_encoding(self):
        """Retrieve encoding as list from JSON string"""
        if self.face_encoding:
            return json.loads(self.face_encoding)
        return None    

class ModerationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.OneToOneField(MissingPersonReport, on_delete=models.CASCADE, related_name='moderation_log')
    action = models.CharField(max_length=10)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderated_reports')
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(null=True, blank=True)

class ReportMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(MissingPersonReport, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"From {self.sender.username} regarding {self.report.name} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"