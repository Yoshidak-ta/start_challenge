from django.shortcuts import render, redirect
from . import forms
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime
from accounts.models import Users
from accounts.forms import ObjectiveRegistForm, ObjectiveEditForm, SearchForm
from .models import Schedules, ToDos, SchedulesHistory
from .utils.calendar_helper import CalendarHelper
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.views.decorators.csrf import csrf_exempt

# スケジュール画面
@login_required
def schedule(request, year=None, month=None):
  todos = ToDos.objects.filter(user=request.user, is_completed=False)

  todo_list_form = forms.ToDoListForm()
  user = Users.objects.get(pk=request.user.id)
  objective = user.objective
  objective_due_date = user.objective_due_date

  now = localtime()
  due = localtime(objective_due_date)
  delta = due - now
  total_seconds = int(delta.total_seconds())
  limit = (due.date() - now.date()).days
  objective_regist_form = ObjectiveRegistForm()
  objective_edit_form = ObjectiveEditForm()
  today = datetime.now()
  year = int(year or datetime.now().year)
  month = int(month or datetime.now().month)

  if month < 1:
    year -= 1
    month = 12
  elif month > 12:
    year += 1
    month = 1

  calendar_helper = CalendarHelper(year, month)
  month_calendar = calendar_helper.generate_month_calendar()
  first_day, last_day = calendar_helper.get_month_days()

  schedules = Schedules.objects.filter(user=user)
  for s in schedules:
    s.start_date_jst = localtime(s.start_at).date()
    s.end_date_jst = localtime(s.end_at).date()

  return render(request, 'schedules/schedule.html', context={
    'today':today,
    'year':year, 
    'month':month,
    'limit':limit,
    'total_seconds':total_seconds,
    'month_calendar':month_calendar, 
    'schedules':schedules, 
    'todos':todos,
    'todo_list_form':todo_list_form,
    'objective':objective,
    'objective_due_date':objective_due_date,
    'objective_regist_form':objective_regist_form,
    'objective_edit_form':objective_edit_form,
  })

# スケジュール詳細画面
@login_required
def schedule_show(request, year=None, month=None, day=None):
  year = year
  month = month
  day = day

  try:
    date_value = datetime(year, month, day)
  except ValueError:
    date_value = None
  
  initial_data = {}
  if date_value:
    initial_data = {
      'start_at': date_value,
      'end_at': date_value,
    }
  schedule_regist_form = forms.ScheduleRegistForm(initial=initial_data)
  schedule_edit_form = forms.ScheduleEditForm()
  fields_left = ['start_at', 'end_at']
  fields_right = ['task', 'place', 'user']
  users = Users.objects.filter(is_staff=False)
  schedule_history = SchedulesHistory.objects.all()
  formatted_date = datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d').date()
  schedules = Schedules.objects.prefetch_related('user').filter(
    start_at__date__lte=formatted_date,
    end_at__date__gte=formatted_date,
  )
  searchform = SearchForm(request.GET or None)
  results = Users.objects.all()

  if searchform.is_valid():
    query = searchform.cleaned_data.get('query')
    if query:
      results = results.filter(
        models.Q(username__icontains=query)
      )
  
  return render(request, 'schedules/schedule_show.html', context={
    'year':year,
    'month':month,
    'day':day,
    'users':users,
    'schedule_regist_form':schedule_regist_form,
    'schedule_edit_form':schedule_edit_form,
    'fields_left':fields_left,
    'fields_right':fields_right,
    'schedule_history':schedule_history,
    'formatted_date':formatted_date,
    'schedules':schedules,
    'searchform':searchform,
    'results':results
  })

# ToDoリストタスク追加
@login_required
def add_todo(request, year=None, month=None):
  year = year
  month = month
  if request.method == 'POST':
    todo_list_form = forms.ToDoListForm(request.POST or None)
    if todo_list_form.is_valid():
      todo = todo_list_form.save(commit=False)
      todo.user = request.user
      todo.save()

      return JsonResponse({
        'success':True,
        'task':todo.task,
        'due_date':todo.due_date.strftime('%Y-%m-%d'),
        'priority':todo.get_priority_display(),
        'todo_id':todo.id
      })
    else:
      # messages.error(request, 'ToDoタスク登録に失敗しました。以下をご確認ください。')
      # for field, errors in todo_list_form.errors.items():
      #   for error in errors:
      #     messages.error(request, f"{todo_list_form.fields[field].label}:{error}")
      # return redirect(request, 'schedules:schedule', year=year, month=month)
      
      return JsonResponse({
        'success': False, 
        'errors': {
          todo_list_form.fields[field].label: [str(error) for error in errors]
          for field, errors in todo_list_form.errors.items()
        }
      })
  else:
    return redirect(request, 'schedules:schedule', year=year, month=month)
    # return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# ToDoリストタスク達成
@login_required
@csrf_exempt
def complete_todo(request, year, month, todo_id):
  year = year
  month = month
  if request.method == 'POST':
    user = request.user
    todo = get_object_or_404(ToDos, id=todo_id, user=request.user)
    if todo.priority == 1:
      user.rank += 3
    elif todo.priority == 2:
      user.rank += 2
    else:
      user.rank += 1
    todo.is_completed = True
    todo.save()
    user.save()
    return JsonResponse({'success':True})
  return JsonResponse({'success':False, 'error':'Invalid request.'}, status=400)

# スケジュール登録
@login_required
def schedule_regist(request):
  year = datetime.now().year
  month = datetime.now().month
  day = datetime.now().day

  if request.method == "POST":
    schedule_regist_form = forms.ScheduleRegistForm(request.POST)
    print(schedule_regist_form)
    if schedule_regist_form.is_valid():
      selected_user_ids = set(request.POST.getlist('schedule_user'))
      print('登録ユーザー：', selected_user_ids)
      if not selected_user_ids:
        messages.error(request, 'スケジュール登録に失敗しました。以下をご確認ください。')
        messages.error(request, '登録ユーザー：ユーザーを選択してください')
        return redirect('schedules:schedule', year=year, month=month)
      
      regist = schedule_regist_form.save(commit=False)
      try:
        regist.start_at = datetime.strptime(request.POST['start_at'], '%Y-%m-%dT%H:%M')
        regist.end_at = datetime.strptime(request.POST['end_at'], '%Y-%m-%dT%H:%M') 
      except ValueError:
        print(regist.start_at, regist.end_at)
        messages.error(request, "日付のフォーマットが不正です。")
        return redirect('schedules:schedule_show', year=year, month=month, day=day)
      regist.save()

      selected_user_ids = [int(uid.strip()) for uid in selected_user_ids if str(uid).strip().isdigit()]
      print('登録ユーザーid：', selected_user_ids)
      regist.user.set(Users.objects.filter(id__in=selected_user_ids))

      messages.info(request, 'スケジュールが登録されました。')
      return redirect('schedules:schedule_show', year=regist.start_at.year, month=regist.start_at.month, day=regist.start_at.day)

    else:
      messages.error(request, 'スケジュール登録に失敗しました。以下をご確認ください。')

      for field, errors in schedule_regist_form.errors.items():
        for error in errors:
          messages.error(request, f"{schedule_regist_form.fields[field].label}:{error}")
      
      print('エラー発生', schedule_regist_form.errors)
      return redirect('schedules:schedule', year=year, month=month)

  else:    
    schedule_regist_form = forms.ScheduleRegistForm()

  return redirect('schedules:schedule_show', year=year, month=month, day=day)

# スケジュール編集
@login_required
def schedule_edit(request, pk):
  schedule = get_object_or_404(Schedules, pk=pk)
  if request.method == 'POST':
    schedule_edit_form = forms.ScheduleEditForm(request.POST or None, instance=schedule)
    if schedule_edit_form.is_valid():
      schedule_edit_form.save(commit=False)
      schedule.updated_at = datetime.now()
      schedule.save()
      
      selected_user_ids = set(request.POST.getlist('edit_user'))
      print('編集ユーザー：', selected_user_ids)
      selected_user_ids = [int(uid.strip()) for uid in selected_user_ids if str(uid).strip().isdigit()]
      print('編集ユーザーids：', selected_user_ids)
      if selected_user_ids:
        schedule.user.set(Users.objects.filter(id__in=selected_user_ids))
      else:
        schedule.user.clear()
      
      # 編集履歴取得
      SchedulesHistory.objects.create(
        schedule=schedule,
        user=request.user,
        updated_at=timezone.now()
      )

      messages.info(request, 'スケジュールを編集しました')
      return redirect('schedules:schedule_show', year=schedule.start_at.year, month=schedule.start_at.month, day=schedule.start_at.day)
    
    else:
      messages.error(request, 'スケジュール編集に失敗しました。')

      for field, errors in schedule_edit_form.errors.items():
        for error in errors:
          messages.error(request, f"{schedule_edit_form.fields[field].label}:{error}")
      
      print('エラー発生', schedule_edit_form.errors)

  return redirect('schedules:schedule_show', year=schedule.start_at.year, month=schedule.start_at.month, day=schedule.start_at.day)

# スケジュールpk取得
@login_required
def get_schedule_data(request, pk):
  schedule = get_object_or_404(Schedules, pk=pk)
  user_ids = list(schedule.user.values_list('id', flat=True))
  usernames = list(schedule.user.values_list('username', flat=True))
  return JsonResponse({'user_ids': user_ids, 'usernames': usernames, 'start_at':schedule.start_at.isoformat(), 'end_at': schedule.end_at.isoformat()})

# スケジュール更新履歴取得
@login_required
def get_schedule_history(request, pk):
  schedule = get_object_or_404(Schedules, pk=pk)
  history = SchedulesHistory.objects.filter(schedule=schedule).order_by('-updated_at')

  print(f'取得対象スケジュール：{pk}')
  print(f'履歴取得件数：{history.count()}')

  if history.exists():
    history_data = [
      {
        'user': entry.user.username,
        'updated_at': entry.updated_at.strftime('%Y-%m-%d %H:%M')
      }
      for entry in history
    ]
    print(f"履歴データ: {history_data}")
    return JsonResponse({'success':True, 'history': history_data})
  else:
    print("履歴なし")
    return JsonResponse({'success':False, 'history': []})

# スケジュール削除
@login_required
def schedule_delete(request, pk):
  schedule = get_object_or_404(Schedules, pk=pk)
  schedule.delete()
  messages.info(request, 'スケジュールが削除されました')
  return redirect('schedules:schedule_show', year=schedule.start_at.year, month=schedule.start_at.month, day=schedule.start_at.day)

# 目標設定
@login_required
def objective_regist(request):
  user = request.user
  # year = datetime.now().year
  # month = datetime.now().month
  if request.method == 'POST':
    regist = ObjectiveRegistForm(request.POST, instance=user)
    if regist.is_valid():
      regist.save()
      messages.info(request, '目標を設定しました')
      return JsonResponse({'success': True, 'objective': regist.cleaned_data['objective']})
    
    else:
      messages.error(request, '目標設定に失敗しました。以下をご確認ください。')
      for field, errors in regist.errors.items():
        for error in errors:
          messages.error(request, f"{regist.fields[field].label}:{error}")
      
      print('エラー発生', regist.errors)
      return JsonResponse({'success': False, 'errors': regist.errors}, status=400)
    

  return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
  

# 目標編集
@login_required
def objective_edit(request, user_id):
  user = get_object_or_404(Users, pk=user_id)
  year = datetime.now().year
  month = datetime.now().month

  if request.method == 'POST':
    objective_edit_form = ObjectiveEditForm(request.POST, instance=user)
    if objective_edit_form.is_valid():
      objective_edit_form.save(commit=False)
      user.updated_at = datetime.now()
      user.save()
      messages.info(request, '目標を編集しました')
      return redirect('schedules:schedule', year=year, month=month)
   
    else:
      messages.error(request, '目標編集に失敗しました。以下をご確認ください。')
      for field, errors in objective_edit_form.errors.items():
        for error in errors:
          messages.error(request, f"{objective_edit_form.fields[field].label}:{error}")
      return redirect('schedules:schedule', year=year, month=month)

# 目標データ取得
@login_required
def get_objective_data(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
    return JsonResponse({'objective': user.objective, 'objective_due_date': user.objective_due_date.strftime('%Y-%m-%d %H:%M')})
  except Users.DoseNotExist:
    raise Http404('ユーザーが見つかりません')

# 目標達成
@login_required
def objective_goal(request, pk):
  year = datetime.now().year
  month = datetime.now().month
  if request.method == 'POST':
    user = get_object_or_404(Users, pk=pk)
    user.objective = None
    user.objective_due_date = None
    user.rank += 10
    user.save()
    messages.info(request, '目標を達成しました')
    return redirect('schedules:schedule', year=year, month=month)
