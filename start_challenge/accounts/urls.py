from django.urls import path
from . import views
from django.conf.urls import include

app_name = 'accounts'

urlpatterns = [
  path('', views.home, name='home'),
  path('user_regist', views.user_regist, name='user_regist'),
  path('user_login', views.user_login, name='user_login'),
  path('user_logout', views.user_logout, name='user_logout'),
  path('user_edit', views.user_edit, name='user_edit'),
  path('reset_password', views.reset_password, name='reset_password'),
  path('user_delete', views.user_delete, name='user_delete'),
  path('users/', views.users, name='users'),
  path('users/user_show/<int:pk>', views.user_show, name='user_show'),
  path('user/notification_data', views.notification_data, name='notification_data'),
  path('user/mark_notification_sent', views.mark_notification_sent, name='mark_notification_sent'),
]
