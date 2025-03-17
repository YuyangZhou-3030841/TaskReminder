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
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )

    title = models.CharField("任务名称", max_length=200)
    description = models.TextField("任务描述", blank=True)
    priority = models.CharField("优先级", max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    start_date = models.DateTimeField("开始日期", null=True, blank=True)  # 如果需要
    due_date = models.DateTimeField("截止日期")
    is_completed = models.BooleanField("是否完成", default=False)

    # 任务属于哪个用户
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title

    @property
    def is_expiring_soon(self):
        """
        判断任务是否即将到期：距离当前时间 <= 7 天
        """
        return 0 <= (self.due_date - timezone.now()).days <= 7

    @property
    def is_overdue(self):
        """
        判断任务是否已过期：截止时间早于当前时间
        """
        return self.due_date < timezone.now()

    @property
    def reminder_time(self):
        """
        在截止时间的 2 小时前提醒
        """
        return self.due_date - timedelta(hours=2)