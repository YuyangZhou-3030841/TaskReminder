import os
from celery import Celery

# 设置 Django 的 settings 模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_reminder.settings")

app = Celery("task_reminder")
# 从 Django 的 settings.py 中加载 celery 配置，配置前缀为 CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")
# 自动发现各 app 下的 tasks.py 文件
app.autodiscover_tasks()
