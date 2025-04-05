from django.shortcuts import render, redirect
from .models import Chats, ChatsGroup
from . import forms
from schedules.forms import ScheduleRegistForm
from django.shortcuts import get_object_or_404
from accounts.models import Users
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


# チャット共通コンテキスト
def get_chat_context(request, group):
  chats = Chats.objects.filter(chatsgroup=group).order_by('created_at')
  chat_form = forms.ChatRegistForm()
  chat_group_form = forms.ChatsGroupForm()
  chatgroups = ChatsGroup.objects.filter(group_category=2, user=request.user)
  private = ChatsGroup.objects.filter(group_category=3)
  users = Users.objects.all()
  schedule_regist_form = ScheduleRegistForm()
  private_user = set()
  for private in private:
    private_user.update(private.user.all())
  fields_left = ['start_at', 'end_at']
  fields_right = ['task', 'place', 'user']
  schedule_regist_form.fields['user'].queryset = Users.objects.all()

  context = {
    'group':group,
    'chats':chats,
    'chatgroups':chatgroups,
    'chat_form':chat_form,
    'chat_group_form':chat_group_form,
    'private':private,
    'private_user':list(private_user),
    'users':users,
    'schedule_regist_form':schedule_regist_form,
    'fields_right':fields_right,
    'fields_left':fields_left,
  }
  return context

# 全体共有チャット
@login_required
def share_chat(request):
  share_chat = get_object_or_404(ChatsGroup, group_category=1)
  if request.user not in share_chat.user.all():
    share_chat.user.add(request.user)
  
  context = get_chat_context(request, share_chat)
  additional_context = {
      'share_chat':share_chat,
    }
  context.update(additional_context)
  return render(request, 'chats/share_chat.html', context)

# グループチャット
@login_required
def group_chat(request, group_id):
  group = get_object_or_404(ChatsGroup, pk=group_id, group_category=2)

  group_user_ids = set(group.user.values_list('id', flat=True))

  context = get_chat_context(request, group)
  additional_context = {
      'group':group,
      'group_user_ids':group_user_ids,
    }
  context.update(additional_context)
  return render(request, 'chats/group_chat.html', context)

# 個人チャット
@login_required
def private_chat(request, user_id):
  target_user = get_object_or_404(Users, pk=user_id)
  user_ids = sorted([request.user.id, target_user.id])
  groupname = f"private_chat_{user_ids[0]}_{user_ids[1]}"
  private_group, created = ChatsGroup.objects.get_or_create(
    group_category=3,
    groupname=groupname
  )
  private_group.user.add(request.user, target_user)

  context = get_chat_context(request, private_group)
  additional_context = {
      'target_user':target_user,
      'private_group':private_group,
    }
  context.update(additional_context)

  return render(request, 'chats/private_chat.html', context)

# グループ作成
@login_required
def chatsgroup_create(request):
  if request.method == 'POST':
    chatsgroup_form = forms.ChatsGroupForm(request.POST, request.FILES or None)
    if chatsgroup_form.is_valid():
      new_group = chatsgroup_form.save(commit=False)
      new_group.group_category = 2
      new_group.save()
      new_group_id = new_group.id
      print(new_group_id)

      selected_user_ids_str = request.POST.get('group_users', '')
      selected_user_ids = selected_user_ids_str.split(',') if selected_user_ids_str else []
      valid_user_ids = [int(user_id.strip()) for user_id in selected_user_ids if user_id.strip().isdigit()]
      if selected_user_ids:
        new_group.user.set(Users.objects.filter(id__in=valid_user_ids))
      else:
        new_group.user.clear()

      messages.info(request, 'グループが作成されました')
      return redirect('chats:group_chat', group_id=new_group_id)
    else:
      print('エラー発生', chatsgroup_form.errors)

  else:
    messages.error(request, '入力事項に誤りがあります')

  return redirect('chats:share_chat') 

# メッセージ送信
@login_required
def send_message(request):
  if request.method == 'POST':
    chat_form = forms.ChatRegistForm(request.POST, request.FILES)
    group_id = request.POST.get('group_id')
    group = get_object_or_404(ChatsGroup, id=group_id)
    user = group.user

    if chat_form.is_valid():
      chat = chat_form.save(commit=False)
      chat.user = request.user
      chat.chatsgroup = group
      chat.save()
      
      if group.group_category == 1:
        return redirect('chats:share_chat')
      elif group.group_category == 2:
        return redirect('chats:group_chat', group_id=group_id)
      elif group.group_category == 3:
        other_user = group.user.exclude(id=request.user.id).first()
        return redirect('chats:private_chat', user_id=other_user.id) if other_user else redirect('chats:share_chat')
    else:
      if group.group_category == 1:
        messages.error(request, '送信に失敗しました')
        return redirect('chats:share_chat')
      elif group.group_category == 2:
        messages.error(request, '送信に失敗しました')
        return redirect('chats:group_chat', group_id=group_id)
      elif group.group_category == 3:
        messages.error(request, '送信に失敗しました')
        return redirect('chats:private_chat', user_id=other_user.id) if other_user else redirect('chats:share_chat')
        
  return redirect('chats:share_chat')

# モーダル内ユーザ検索
def search_users(request):
  search_query = request.GET.get('search', '')
  if search_query:
    users = Users.objects.filter(username__icontains=search_query)
  else:
    users = Users.objects.filter(is_staff=False, is_active=True)

  user_list = [{'id': user.id, 'username': user.username, 'picture': user.picture.url} for user in users]
  return JsonResponse({'users': user_list})

