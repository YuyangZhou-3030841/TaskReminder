from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class CustomUser(AbstractUser):
    """
    Custom user model, extended from Django's built-in AbstractUser.
    Added fields for mobile number, email and region (time zone).
    """
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\+\d{1,3}\d{9,15}$')],
        help_text="Phone number in international format, e.g. +123456789012"
    )
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=50, blank=True, help_text="User region/timezone")

    def __str__(self):
        return self.username


class Task(models.Model):
    """
    Task Model: Record user's task information, including task name, description, priority, start date, deadline and completion status.
    It also provides some auxiliary attributes, such as whether the task is about to expire, whether it has expired and the reminder time (2 hours before the deadline).
    """
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title

    @property
    def is_expiring_soon(self):
        """
        Determines if the task is about to expire: within 7 days of the deadline (and not expired).
        """
        delta = self.due_date - timezone.now()
        return 0 <= delta.days <= 7

    @property
    def is_overdue(self):
        """
        Determine if the task has expired: the deadline is earlier than the current time.
        """
        return self.due_date < timezone.now()

    @property
    def reminder_time(self):
        """
        Reminder: 2 hours before the task is due.
        """
        return self.due_date - timedelta(hours=2)
