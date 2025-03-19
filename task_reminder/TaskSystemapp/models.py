# TaskSystemapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from django.conf import settings 
def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\+\d{1,3}\d{9,15}$')]
    )
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username

# models.py


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    title = models.CharField("Task name", max_length=200)
    description = models.TextField("Mission statement", blank=True)
    priority = models.CharField("Priority", max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField("Creation time", auto_now_add=True)
    start_date = models.DateTimeField("Start date", null=True, blank=True) 
    due_date = models.DateTimeField("Deadline")
    is_completed = models.BooleanField("Completion", default=False)

    # Which user the task belongs to
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title

    @property
    def is_expiring_soon(self):
        """
        Determine if a task is about to expire: <= 7 days from current time.
        """
        return 0 <= (self.due_date - timezone.now()).days <= 7

    @property
    def is_overdue(self):
        """
        Determining whether a task has expired: deadline is earlier than the current time
        """
        return self.due_date < timezone.now()

    @property
    def reminder_time(self):
        """
        Reminder 2 hours before deadline
        """
        return self.due_date - timedelta(hours=2)