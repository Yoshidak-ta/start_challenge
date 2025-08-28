from django.urls import path
from chats.views import search_users
from . import views

app_name = 'schedules'

urlpatterns = [
  path('schedule/<int:year>/<int:month>', views.schedule, name='schedule'),
  path('schedule_show/<int:year>/<int:month>/<int:day>', views.schedule_show, name='schedule_show'),
  path('schedule/<int:year>/<int:month>/add_todo/', views.add_todo, name='add_todo'),
  path('todo_edit/<int:pk>', views.todo_edit, name='todo_edit'),
  path('todo_delete/<int:pk>', views.todo_delete, name='todo_datele'),
  path('get_todo_task/<int:pk>', views.get_todo_task, name='get_todo_task'),
  path('schedule/<int:year>/<int:month>/complete_todo/<int:todo_id>', views.complete_todo, name='complete_todo'),
  path('schedule_regist', views.schedule_regist, name='schedule_regist'),
  path('schedule_edit/<int:pk>', views.schedule_edit, name='schedule_edit'),
  path('schedule_show/get_schedule_data/<int:pk>', views.get_schedule_data, name='get_schedule_data'),
  path('schedule_delete/<int:pk>', views.schedule_delete, name='schedule_delete'),
  path('schedule_show/search_users', search_users, name='search_users'),
  path('schedule_history/<int:pk>', views.get_schedule_history, name='schedule_history'),
  path('objective_regist/', views.objective_regist, name='objective_regist'),
  path('get_objective_data/<int:user_id>', views.get_objective_data, name='get_objective_data'),
  path('objective_edit/<int:user_id>', views.objective_edit, name='objective_edit'),
  path('objective_goal/<int:pk>', views.objective_goal, name='objective_goal'),
  path('objective_delete/<int:pk>', views.objective_delete, name='objective_delete'),
]