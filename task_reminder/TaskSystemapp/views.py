from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.utils import timezone, translation
from .forms import LoginForm, RegisterForm, QuickTaskForm, DetailedTaskForm, UserUpdateForm
from .models import Task
from .tasks import send_email_task
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
                error = "用户名或密码错误"
    else:
        form = LoginForm()
    return render(request, 'TaskSystemapp/login.html', {'form': form, 'error': error})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)  # 注意接收FILES
        if form.is_valid():
            user = form.save()
            return redirect('login')
        # 表单无效时保留已填数据
    else:
        form = RegisterForm()
    return render(request, 'TaskSystemapp/register.html', {'form': form})

def home(request):
    user = request.user
    # 如果用户已登录且设置了地区（这里假设region存储的是时区字符串）
    if user.is_authenticated and user.region:
        try:
            timezone.activate(user.region)
        except Exception:
            timezone.deactivate()  # 如果激活失败，则使用默认
    # 如有语言偏好字段，可做如下处理（假设user.language为 'zh-hans' 或 'en' 等）
    if user.is_authenticated and hasattr(user, 'language'):
        translation.activate(user.language)
    else:
        translation.activate(settings.LANGUAGE_CODE)
        
    # 获取当前时间（已同步时区）
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

    # 查询当前用户任务（初始查询）
    user_tasks = Task.objects.filter(user=user)
    
    # 如果提供了搜索条件，先过滤出包含搜索关键字的任务，再按照“包含次数”和优先级排序
    if search_query:
        # 将查询结果转换为列表，便于后续在 Python 层做自定义排序
        task_list = list(user_tasks)
        def priority_order(task):
            # 自定义优先级排序，高 -> 中 -> 低
            mapping = {'high': 1, 'medium': 2, 'low': 3}
            return mapping.get(task.priority, 4)
        # 过滤出标题中包含搜索关键词的任务，并统计出现次数（不区分大小写）
        filtered_tasks = []
        for task in task_list:
            count = task.title.lower().count(search_query.lower())
            if count > 0:
                filtered_tasks.append((task, count))
        # 按照出现次数降序、然后按优先级排序（优先级值小的排前面）
        filtered_tasks.sort(key=lambda x: (-x[1], priority_order(x[0])))
        # 取出排序后的任务对象列表
        user_tasks = [item[0] for item in filtered_tasks]
    else:
        # 根据状态过滤
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
        # 默认按截止时间排序
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
        'current_time': current_time,  # 用于日历显示
        'search_query': search_query,
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

def user_profile(request):
    # 单独的用户详情页，展示并允许修改用户信息
    return render(request, 'TaskSystemapp/profile.html', {'user': request.user})

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
    return JsonResponse({'success': False, 'error': '无效的请求方式'})

def quick_add_task(request):
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            # 邮件提醒：截止前2小时提醒
            reminder_time = task.due_date - timedelta(hours=2)
            now = timezone.now()
            if reminder_time > now:
                subject = f"任务提醒：{task.title}"
                message = f"你的任务 '{task.title}' 将于 {task.due_date.strftime('%Y-%m-%d %H:%M')} 到期，请及时处理。"
                recipient_list = [request.user.email]
                send_email_task.apply_async((subject, message, recipient_list), eta=reminder_time)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('home')

def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'TaskSystemapp/profile.html', {'form': form, 'user': request.user})

def custom_logout(request):
    logout(request)
    return redirect('login')

def set_language(request, lang_code):
    if request.method == 'POST':
        if lang_code in [code for code, _ in settings.LANGUAGES]:
            translation.activate(lang_code)
            response = JsonResponse({'status': 'success'})
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=365*24*60*60
            )
            return response
    return JsonResponse({'status': 'error'}, status=400)