from django.shortcuts import render, redirect
from . import forms
from django.core.exceptions import ValidationError
from .models import UserActivateTokens, Users, WebPushSubscription
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime
from questions.models import Questions, Answers
from django.shortcuts import get_object_or_404
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from pywebpush import webpush, WebPushException
import json
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
  if user_regist_form.is_valid():
     try:
       user_regist_form.save()
       messages.info(request, 'ご登録のメールアドレスに送信されました。メッセージのURLをクリックして会員登録を完了させてください。')
       return redirect('accounts:user_login')
     except ValidationError as e:
       user_regist_form.add_error('password', e)
       user_regist_form.add_error('email', e)
       messages.warning(request, '入力事項に誤りがあります')
       print(user_regist_form.errors)
  else:
     print(user_regist_form.errors)
  
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
    user.updated_at = datetime.now()
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

# プッシュ通知登録
@csrf_exempt  # CSRF チェックを無効化（必要に応じて）
@login_required
def register_push(request):
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      endpoint = data.get('endpoint')
      p256dh_key = data.get('keys', {}).get('p256dh')

      if not endpoint or not p256dh_key:
        return JsonResponse({'error': 'Missing endpoint'}, status=400)
      
      subscription, created = WebPushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={'p256dh_key': p256dh_key},
        user = request.user
      )
      
      if created:
        return JsonResponse({'message': 'Subscription created'}, status=201)
      else:
        return JsonResponse({'message': 'Subscription updated'}, status=200)
    
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
    except Exception as e:
      return JsonResponse({'error': str(e)}, status=500)
  
  return JsonResponse({'error': 'Invalid request'}, status=400)

# プッシュ通知送信
@login_required
def send_push_notification(title, message):
  subscriptions = WebPushSubscription.objects.all()
  payload = json.dumps({'title': title, 'message': message})
  print(f'通知送信開始：{title} - {message}')

  for sub in subscriptions:
    print(f'通知送信：{sub.endpoint}')
    try:
      webpush(
        subscription_info={
          'endpoint': sub.endpoint,
          'keys': {
            'p256dh': sub.p256dh_key
          }
        },
        data=payload,
        vapid_private_key=settings.VAPID_PRIVATE_KEY,
        vapid_claims={'sub':'mailto:bsk.gooserock@gmail.com'}
      )
      print('通知送信成功')
    except WebPushException as e:
      print(f'プッシュ通知の送信に失敗しました： {str(e)}')

# プッシュ通知解除
@csrf_exempt
@login_required
def unregister_subscription(request):
    if request.method == "POST":
        try:
          data = json.loads(request.body)
          print(f'受信データ：{data}')
          endpoint = data.get("endpoint")

          if not endpoint:
            return JsonResponse({'error': 'エンドポイントが提供されていません'}, status=400)

          subscription = WebPushSubscription.objects.filter(endpoint=endpoint)
          if subscription.exists():
            print(f'削除対象：{subscription}')
            subscription.delete()
            return JsonResponse({'message': '登録解除成功'}, status=200)
          else:
            return JsonResponse({'error': '登録が見つかりません'}, status=404)
        
        except json.JSONDecodeError:
          return JsonResponse({'error': '無効なJSON'}, status=400)
        
    return JsonResponse({"message": "無効なリクエスト"}, status=405)
