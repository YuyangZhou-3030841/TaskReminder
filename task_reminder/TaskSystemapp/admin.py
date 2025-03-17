# TaskSystemapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'region')
    search_fields = ('username', 'email', 'phone')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'phone', 'region', 'avatar')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)