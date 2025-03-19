from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.utils import timezone, translation
from .forms import LoginForm, RegisterForm, QuickTaskForm, DetailedTaskForm, UserUpdateForm
from .models import Task, CustomUser
from django.conf import settings

def custom_login(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = "Incorrect username or password"
    else:
        form = LoginForm()
    return render(request, 'TaskSystemapp/login.html', {'form': form, 'error': error})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'TaskSystemapp/register.html', {'form': form})

def home(request):
    # Recapture the latest user instance (if authenticated)
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.pk)
    else:
        user = request.user

    # Synchronise user time zones
    if user.is_authenticated and user.region:
        try:
            timezone.activate(user.region)
        except Exception:
            timezone.deactivate()
    if user.is_authenticated and hasattr(user, 'language'):
        translation.activate(user.language)
    else:
        translation.activate(settings.LANGUAGE_CODE)

    current_time = timezone.now()

    filter_status = request.GET.get('status', 'unfinished')
    search_query = request.GET.get('search', '').strip()
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            current_date = current_time
    else:
        current_date = current_time

    # Filtering of tasks based on user-selected dates 
    user_tasks = Task.objects.filter(user=user, due_date__date=current_date.date())

    if search_query:
        task_list = list(user_tasks)
        def priority_order(task):
            mapping = {'high': 1, 'medium': 2, 'low': 3}
            return mapping.get(task.priority, 4)
        filtered_tasks = []
        for task in task_list:
            count = task.title.lower().count(search_query.lower())
            if count > 0:
                filtered_tasks.append((task, count))
        filtered_tasks.sort(key=lambda x: (-x[1], priority_order(x[0])))
        user_tasks = [item[0] for item in filtered_tasks]
    else:
        if filter_status == 'completed':
            user_tasks = user_tasks.filter(is_completed=True)
        elif filter_status == 'unfinished':
            user_tasks = user_tasks.filter(is_completed=False)
        elif filter_status == 'expiring':
            user_tasks = user_tasks.filter(
                is_completed=False,
                due_date__lte=current_time + timedelta(days=7),
                due_date__gte=current_time
            )
        user_tasks = user_tasks.order_by('due_date')

    sidebar_tasks = user_tasks

    soon_expiring_tasks = Task.objects.filter(
        user=user,
        is_completed=False,
        due_date__lte=current_time + timedelta(days=7),
        due_date__gte=current_time
    ).order_by('due_date')

    selected_task_id = request.GET.get('task_id')
    selected_task = None
    if selected_task_id:
        try:
            selected_task = Task.objects.get(pk=selected_task_id, user=user)
        except Task.DoesNotExist:
            selected_task = None

    context = {
        'sidebar_tasks': sidebar_tasks,
        'soon_expiring_tasks': soon_expiring_tasks,
        'selected_task': selected_task,
        'quick_form': QuickTaskForm(),
        'detailed_form': DetailedTaskForm(),
        'current_time': current_time,
        'search_query': search_query,
        'user': user,
    }
    return render(request, 'TaskSystemapp/home.html', context)

def task_events(request):
    tasks = Task.objects.filter(user=request.user)
    events = []
    for task in tasks:
        events.append({
            'title': task.title,
            'start': task.due_date.isoformat(),
            'color': '#4CAF50' if task.is_completed else '#FF5722'
        })
    return JsonResponse(events, safe=False)

def detailed_add_task(request):
    if request.method == 'POST':
        form = DetailedTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('home')

def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.is_completed = True
    task.save()
    return redirect('home')

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('home')
    return JsonResponse({'success': False, 'error': 'Invalid modalities of request'})

def quick_add_task(request):
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('home')

def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.refresh_from_db()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'TaskSystemapp/profile.html', {'form': form, 'user': request.user})

def custom_logout(request):
    logout(request)
    return redirect('login')
