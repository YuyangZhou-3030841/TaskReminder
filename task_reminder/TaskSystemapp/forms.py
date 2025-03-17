from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import Task

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="电子邮箱",
        help_text="请输入有效的邮箱地址"
    )
    phone = forms.CharField(
        required=True,
        max_length=15,
        label="手机号码",
        help_text="国际格式（例：+8613812345678）"
    )
    avatar = forms.ImageField(
        required=False,
        label="用户头像",
        help_text="可选，建议尺寸 200x200 像素"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'region', 'avatar']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已被注册")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+'):
            raise forms.ValidationError("请使用国际格式（例如：+86开头）")
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("该手机号已被注册")
        return phone
    # task_reminder/TaskSystemapp/forms.py




class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # 快速添加只需填写任务名称、优先级和截止时间
        fields = ['title', 'priority', 'due_date']
        widgets = {
            # 使用 datetime-local 输入类型，使浏览器显示选择器
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DetailedTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # 详细添加需填写任务名称、优先级、开始日期、截止日期和任务描述
        fields = ['title', 'priority', 'start_date', 'due_date', 'description']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'region', 'avatar']
