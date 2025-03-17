# TaskSystemapp/urls.py
from django.urls import path
from .views import custom_login, register,home,quick_add_task,detailed_add_task,delete_task,profile,complete_task, custom_logout
from django.conf import settings          # 导入设置
from django.conf.urls.static import static  # 导入静态文件处理函数
urlpatterns = [
    path('login/', custom_login, name='login'),
    path('register/', register, name='register'),
    path('home/', home, name='home'),
    path('quick-add/', quick_add_task, name='quick_add_task'),
    path('detailed-add/', detailed_add_task, name='detailed_add_task'),
    path('delete-task/<int:task_id>/', delete_task, name='delete_task'),
     path('profile/', profile, name='profile'),
    path('complete-task/<int:task_id>/', complete_task, name='complete_task'),
     path('logout/', custom_logout, name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)