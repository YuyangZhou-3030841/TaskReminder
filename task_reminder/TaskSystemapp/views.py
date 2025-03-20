from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.utils import timezone, translation
from django.conf import settings
from .forms import LoginForm, RegisterForm, QuickTaskForm, DetailedTaskForm, UserUpdateForm
from .models import Task, CustomUser

def custom_login(request):
    """
    User Login View: Use LoginForm to validate username and password, jump to homepage after successful login.
    Returns an error message if login fails.
    """
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
    """
    User Registration View: Use RegisterForm to create a new user and jump to login page after successful registration.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'TaskSystemapp/register.html', {'form': form})


def home(request):
    """
    Home view:
    - Synchronise user's time zone and language settings
    - Filter tasks based on start_date, end_date and search criteria in URL parameters
    - Get the list of tasks in the sidebar, upcoming tasks, and selected tasks
    - Pass each form object to the template for rendering.
    """
    user = request.user
    if user.is_authenticated:
        # Get up-to-date user information and ensure that time zones and language settings are synchronised
        user = CustomUser.objects.get(pk=user.pk)

    # Synchronise user time zone and language settings
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
    search_query = request.GET.get('search', '').strip()

    # Parses the date parameter passed in the URL
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return None

    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    if not start_date or not end_date:
        start_date = current_time.date()
        end_date = current_time.date() + timedelta(days=7)

    # Filter tasks for the current user within a specified date range
    user_tasks = Task.objects.filter(
        user=user,
        due_date__date__gte=start_date,
        due_date__date__lte=end_date
    )

    # Filter tasks by search keywords
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
        user_tasks = user_tasks.order_by('due_date')

    all_tasks = user_tasks  # For sidebar and search results display

    # Get tasks that are about to expire (current time up to 7 days and not completed)
    soon_expiring_tasks = Task.objects.filter(
        user=user,
        is_completed=False,
        due_date__lte=current_time + timedelta(days=7),
        due_date__gte=current_time
    ).order_by('due_date')

    # Selected task (specified by URL parameter task_id)
    selected_task = None
    selected_task_id = request.GET.get('task_id')
    if selected_task_id:
        try:
            selected_task = Task.objects.get(pk=selected_task_id, user=user)
        except Task.DoesNotExist:
            selected_task = None

    context = {
        'all_tasks': all_tasks,
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
    """
    Returns a calendar event (in JSON format) for the current user task, for front-end calendar display.
    """
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
    """
    Detailed Add Task View: Receive AJAX submitted form data, save the task and return the task deadline.
    """
    if request.method == 'POST':
        form = DetailedTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            task_deadline = task.due_date.strftime("%Y-%m-%d %H:%M")
            return JsonResponse({'success': True, 'task_deadline': task_deadline})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('home')


def complete_task(request, task_id):
    """
    Marks the specified task as completed and redirects back to the home page.
    """
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.is_completed = True
    task.save()
    return redirect('home')


def delete_task(request, task_id):
    """
    Deletes the specified task.Support AJAX request, return JSON data when successful, otherwise redirect back to the home page.
    """
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('home')
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def quick_add_task(request):
    """
    Quick Add Task View: Receive AJAX form data, save the task and return the task deadline.
    """
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            task_deadline = task.due_date.strftime("%Y-%m-%d %H:%M")
            return JsonResponse({'success': True, 'task_deadline': task_deadline})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('home')


def profile(request):
    """
    User Profile View: Allows users to update their personal information.
    Refresh the page after successful update, otherwise show current form error.
    """
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
    """
    The user logs out of the login and is redirected to the login page.
    """
    logout(request)
    return redirect('login')
