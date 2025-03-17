# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Task
from django.conf import settings 

@shared_task
def check_priority_tasks():
    critical_tasks = Task.objects.filter(
        due_date__lte=datetime.now() + timedelta(hours=2),
        priority='H',
        completed=False
    )
    for task in critical_tasks:
        send_mail(
            '任务即将到期提醒',
            f'您的任务"{task.title}"将在2小时内到期',
            'system@example.com',
            [task.user.email],
            fail_silently=False
        )
        # TaskSystemapp/tasks.py
# TaskSystemapp/tasks.py


@shared_task
def send_email_task(subject, message, recipient_list):
    """
    发送邮件的 Celery 任务
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # 发件人地址，需要在 settings.py 中配置
        recipient_list,
        fail_silently=False,
    )



