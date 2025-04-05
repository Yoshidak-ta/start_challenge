from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
  path('chat/share', views.share_chat, name='share_chat'),
  path('chat/group/<int:group_id>', views.group_chat, name='group_chat'),
  path('chat/private/<int:user_id>', views.private_chat, name='private_chat'),
  path('chat/chatsgroup_create/', views.chatsgroup_create, name='chatsgroup_create'),
  path('chat/send_message', views.send_message, name='send_message'),
  path('chat/search_users', views.search_users, name='search_users'),
]