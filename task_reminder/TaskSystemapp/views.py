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
    # 获取最新的用户实例（若已认证）
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.pk)
    else:
        user = request.user

    # 同步用户时区与语言设置
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
    # 获取 start_date 和 end_date 参数（start_date 为今天，end_date 为用户选中的终止日期）
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except Exception:
            start_date = current_time.date()
            end_date = current_time.date() + timedelta(days=7)
    else:
        # 默认：从今天到今天+7天
        start_date = current_time.date()
        end_date = current_time.date() + timedelta(days=7)

    # 筛选用户任务：截止日期在[start_date, end_date]区间内的任务
    user_tasks = Task.objects.filter(
        user=user,
        due_date__date__gte=start_date,
        due_date__date__lte=end_date
    )

    if search_query:
        # 搜索匹配：根据任务标题中出现次数进行降序排序，同时按优先级排序
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

    # 将过滤后的任务列表传给侧边栏（同时也用于搜索结果展示）
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
        'all_tasks': user_tasks,  # 用于侧边栏与搜索结果展示
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
            task_deadline = task.due_date.strftime("%Y-%m-%d %H:%M")
            return JsonResponse({'success': True, 'task_deadline': task_deadline})
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
            task_deadline = task.due_date.strftime("%Y-%m-%d %H:%M")
            return JsonResponse({'success': True, 'task_deadline': task_deadline})
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
