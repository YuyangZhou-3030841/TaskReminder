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
        label="E-mail",
        help_text="Please enter a valid email address"
    )
    phone = forms.CharField(
        required=True,
        max_length=15,
        label="Telephone Number",
        help_text="International format (example: +44 01234 56789-0)"
    )
    avatar = forms.ImageField(
        required=False,
        label="Avatar",
        help_text="Optional, recommended size 200x200 pixels"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'region', 'avatar']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+'):
            raise forms.ValidationError("Please use the international format (e.g., beginning with +44)")
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This mobile phone number has been registered")
        return phone

    def save(self, commit=True):
        # Call the parent class's save method first to generate a user instance (not immediately submitted)
        user = super().save(commit=False)
        # If the user has uploaded an avatar, assign the avatar to the user instance
        if self.cleaned_data.get('avatar'):
            user.avatar = self.cleaned_data.get('avatar')
        if commit:
            user.save()
        return user





class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Quick add just fill in the task name, priority and deadline
        fields = ['title', 'priority', 'due_date']
        widgets = {
            # Use the datetime-local input type to make the browser display the selector
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DetailedTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Detailed additions need to be filled in with task name, priority, start date, deadline and task description
        fields = ['title', 'priority', 'start_date', 'due_date', 'description']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'region', 'avatar']

    def save(self, commit=True):
        user = super().save(commit=False)
        # If the user uploads a new avatar, update the avatar field
        if self.cleaned_data.get('avatar'):
            user.avatar = self.cleaned_data.get('avatar')
        if commit:
            user.save()
        return user

