from django.shortcuts import render, redirect
from . import forms
from django.core.exceptions import ValidationError
from .models import UserActivateTokens, Users
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now
from questions.models import Questions, Answers
from schedules.models import Schedules, ToDos
from django.shortcuts import get_object_or_404
from django.db import models
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
        messages.info(request, 'ご登録のメールアドレスに送信されました。メッセージのURLをクリックして会員登録を完了させてください。')
        return redirect('accounts:user_login')
      except ValidationError as e:
        user_regist_form.add_error('password', e)
        user_regist_form.add_error('email', e)
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

# 会員登録時のトークン発行
def activate_user(request, token):
  user_activated_token = UserActivateTokens.objects.activate_user_by_token(token)
  if hasattr(user_activated_token, 'is_active'):
    if user_activated_token.is_active:
      message = '''
        <div style="height: 50vh; display: flex; justify-content: center; align-items: center; text-align: center;">
          <div>
            <h3>会員登録が完了しました!</h3>
            <a href="http://127.0.0.1:8000/accounts/user_login"">ログイン画面へ戻る</a>
          </div>
        </div>
      '''
    if not user_activated_token.is_active:
      message = '有効化が失敗しています'
  if not hasattr(user_activated_token, 'is_active'):
    message = 'エラーが発生しました'
  return HttpResponse(message)

# ログイン
def user_login(request):
  login_form = forms.LoginForm(request.POST or None)
  if login_form.is_valid():
    email = login_form.cleaned_data.get('email')
    password = login_form.cleaned_data.get('password')
    user = authenticate(email=email, password=password)
    if user:
      if user.is_active:
        login(request, user)
        messages.info(request, 'ログインしました')
        return redirect('accounts:home')
      else:
        messages.warning(request, 'ユーザが仮会員登録状態です。登録を完了させてください。')
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
  today = now().date()

  schedules = Schedules.objects.filter(user=user)
  target_schedules = []
  
  for schedule in schedules:
    start = schedule.start_at.date()
    end = schedule.end_at.date()
    if start <= today and end >= today:
      task = schedule.task
      target_schedules.append(task)

  sub_today = now() + timedelta(hours=9)
  sub_today = sub_today.date()
  tasks_today = ToDos.objects.filter(user=user, due_date=sub_today, is_completed=0).count()
  tasks = ToDos.objects.filter(user=user, is_completed=0).count()

  due_days = None
  if user.objective_due_date:
    objective_date = user.objective_due_date.date()
    due_days = (objective_date - today).days

  data = {
    'schedules': target_schedules,
    'tasks_today': tasks_today,
    'tasks': tasks,
    'due_days': due_days
  }
  return JsonResponse(data)

# ログアウト
@login_required
def user_logout(request):
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
    user_edit_form.save(commit=True)
    user = request.user
    user.updated_at = now()
    user.save()
    messages.info(request, '更新が完了しました')
    return redirect('accounts:home')
  elif request.method == 'POST':  
    messages.warning(request, '更新に失敗しました。もう一度入力してください。')

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

# パスワード再設定
def reset_password(request):
  if request.method == 'POST':
    password_reset_form = forms.PasswordResetForm(request.POST or None)
    if password_reset_form.is_valid():
      try:
        password_reset_form.save()
        messages.info(request, 'パスワードの再設定が完了しました。ログインをおこなってください')
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
  user = get_object_or_404(Users, pk=pk)
  questions = Questions.objects.filter(user=user)
  answers = Answers.objects.filter(user=user)
  
  return render(request, 'accounts/user_show.html', context={
    'user':user, 'questions':questions, 'answers':answers,
  })

logger = logging.getLogger(__name__)