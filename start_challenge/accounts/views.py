from django.shortcuts import render, redirect
from . import forms
from django.core.exceptions import ValidationError
from .models import Users
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils.timezone import now
from questions.models import Questions, Answers
from schedules.models import Schedules, ToDos
from django.shortcuts import get_object_or_404
from django.db import models
from django.views.decorators.csrf import csrf_exempt
import logging

# ホーム画面（Q&A)
def home(request):
  questions = Questions.objects.all().order_by('-created_at')
  qsearchform = forms.QuestionsSearchForm(request.GET or None)
  results = Questions.objects.all()

  if qsearchform.is_valid():
    query = qsearchform.cleaned_data.get('query')
    if query:
      results = results.filter(
        models.Q(title__icontains=query) | models.Q(comment__icontains=query)
      )
    
    category = qsearchform.cleaned_data.get('category')
    if category:
      results = results.filter(category=category)
    
  return render(
    request, 'accounts/home.html', context={
      'questions':questions, 'qsearchform':qsearchform, 'results':results,
    }
  )

# 会員登録
def user_regist(request):
  user_regist_form = forms.UserRegistForm(request.POST or None, request.FILES or None)
  fields_left = ['username', 'email', 'picture', 'password', 'confirm_password']
  fields_right = ['category', 'message']
  if request.method == 'POST':
    if user_regist_form.is_valid():
      try:
        user_regist_form.save()
        email = user_regist_form.cleaned_data.get('email')
        password = user_regist_form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        login(request, user)
        messages.info(request, '会員登録が完了いたしました。ログインを実行し、スタチャレをお楽しみください')
        return redirect('accounts:home')
      except ValidationError as e:
        user_regist_form.add_error('password', e)
        messages.error(request, '会員登録に失敗しました。以下をご確認ください。')
        for field, errors in user_regist_form.errors.items():
            for error in errors:
              messages.error(request, f"{user_regist_form.fields[field].label}:{error}")
        print(user_regist_form.errors)
    else:
      messages.error(request, '会員登録に失敗しました。以下をご確認ください。')
      for field, errors in user_regist_form.errors.items():
          for error in errors:
            if field == '__all__':
              messages.error(request, f'{error}')
            else:
              messages.error(request, f"{user_regist_form.fields[field].label}:{error}")
    
  return render(
    request, 'accounts/user_regist.html', context={
     'user_regist_form': user_regist_form,
     'fields_left': fields_left,
     'fields_right': fields_right
   }
 )

# ログイン
def user_login(request):
  login_form = forms.LoginForm(request.POST or None)
  if login_form.is_valid():
    email = login_form.cleaned_data.get('email')
    password = login_form.cleaned_data.get('password')
    user = authenticate(email=email, password=password)
    if user:
      login(request, user)
      user.notification_sent = True
      user.save()
      messages.info(request, 'ログインしました')
      return redirect('accounts:home')
    else:
      messages.warning(request, 'ユーザまたはパスワードが間違っています。')
  return render(
    request, 'accounts/user_login.html', context={
      'login_form': login_form,
    }
  )

# ログイン時にユーザー情報を取得
@login_required
def notification_data(request):
  user = request.user
  today = now() + timedelta(hours=9)
  today = today.date()
  sub_today = now() + timedelta(hours=9)
  sub_today = sub_today.date()

  schedules = Schedules.objects.filter(user=user)
  target_schedules = []
  
  for schedule in schedules:
    sub_start = schedule.start_at + timedelta(hours=9)
    sub_end = schedule.end_at + timedelta(hours=9)
    start = sub_start.date()
    end = sub_end.date()
    print(start, end)
    if start <= sub_today and end >= sub_today:
      task = schedule.task
      target_schedules.append(task)

  tasks_today = ToDos.objects.filter(user=user, due_date=sub_today, is_completed=0).count()
  tasks = ToDos.objects.filter(user=user, is_completed=0).count()
  notification = user.notification_sent

  due_days = None
  if user.objective_due_date:
    objective_date = user.objective_due_date + timedelta(hours=9)
    objective_date = objective_date.date()
    due_days = (objective_date - today).days

  data = {
    'schedules': target_schedules,
    'tasks_today': tasks_today,
    'tasks': tasks,
    'due_days': due_days,
    'notification': notification,
  }
  return JsonResponse(data)

# ログアウト
@login_required
def user_logout(request):
  user = request.user
  user.notification_sent = True
  logout(request)
  messages.warning(request, 'ログアウトしました')
  return redirect('accounts:home')

# 会員情報編集
@login_required
def user_edit(request):
  user_edit_form = forms.UserEditForm(request.POST or None, request.FILES or None, instance=request.user)
  fields_left = ['username', 'email', 'picture']
  fields_right = ['category', 'message']
  if user_edit_form.is_valid():
    user_edit_form.save(commit=False)
    user = request.user
    user.updated_at = now()
    user.save()
    messages.info(request, '更新が完了しました')
    return redirect('accounts:home')
  elif request.method == 'POST':  
    messages.error(request, '会員情報の編集に失敗しました。以下をご確認ください。')
    for field, errors in user_edit_form.errors.items():
      for error in errors:
        messages.error(request, f"{user_edit_form.fields[field].label}:{error}")

  return render(request, 'accounts/user_edit.html', context={
    'user_edit_form': user_edit_form,
    'fields_left': fields_left,
    'fields_right':fields_right,
  })

# 退会
@login_required
def user_delete(request):
  if request.method == 'POST':
    user = request.user
    #ユーザを無効か
    user.delete()
    #ログアウト
    logout(request)
    messages.info(request, '退会が完了しました。')
    return redirect('accounts:home')

# パスワードリセット
def reset_password(request):
  password_reset_form = forms.PasswordResetForm(request.POST or None)
  if request.method == 'POST':
    if password_reset_form.is_valid():
      try:
        password_reset_form.save()
        messages.info(request, 'パスワードのリセットが完了しました。ログインをおこなってください。')
        return redirect('accounts:user_login')
      except Users.DoesNotExist:
        messages.error(request, 'このメールアドレスは登録されていません。会員登録をおこなってください。')
    else:
      messages.error(request, '入力に誤りがあります。')
  else:
    password_reset_form = forms.PasswordResetForm()

  return render(
    request, 'accounts/reset_password.html', context={
      'password_reset_form':password_reset_form,
    }
  )

# パスワード変更
@login_required
def change_password(request):
  user = request.user
  change_form = forms.ChangePasswordForm(request.POST, user=user)
  if request.method == 'POST':
    if change_form.is_valid():
      change_form.save()
      update_session_auth_hash(request, user)
      messages.info(request, 'パスワードが変更されました。')
      return redirect('accounts:home')
    else:
      messages.error(request, 'パスワードの変更に失敗しました。以下をご確認ください。')
      for field, errors in change_form.errors.items():
        for error in errors:
          if field == '__all__':
            messages.error(request, f'{error}')
          else:
            messages.error(request, f"{change_form.fields[field].label}:{error}")
  else:
    change_form = forms.ChangePasswordForm(user=user)
  
  return render(
    request, 'accounts/change_password.html', context={
      'change_form':change_form,
    }
  )

# ユーザ一覧
def users(request):
  sort_option = request.GET.get('sort', 'username')
  usearchform = forms.UsersSearchForm(request.GET or None)
  results = Users.objects.all()

  if usearchform.is_valid():
    query = usearchform.cleaned_data.get('query')
    if query:
      results = results.filter(
        models.Q(username__icontains=query)
      )
    
    category = usearchform.cleaned_data.get('category')
    if category:
      results = results.filter(category=category)
  
  if sort_option == 'username':
    results = results.order_by('username')
  elif sort_option == 'rank':
    results = results.order_by('-rank')

  return render(request, 'accounts/users.html', context={
    'usearchform':usearchform,
    'results':results,
    'sort_option':sort_option,
  })

# ユーザ詳細
@login_required
def user_show(request, pk):
  target_user = get_object_or_404(Users, pk=pk)
  questions = Questions.objects.filter(user=target_user)
  answers = Answers.objects.filter(user=target_user)
  
  return render(request, 'accounts/user_show.html', context={
    'target_user':target_user, 'questions':questions, 'answers':answers,
  })

logger = logging.getLogger(__name__)

# 通知フラグ
@csrf_exempt
@login_required
def mark_notification_sent(request):
  if request.method == "POST":
    user = request.user
    user.notification_sent = False
    user.save()
    return JsonResponse({"status": "ok"})
  return JsonResponse({"status": "error"}, status=400)