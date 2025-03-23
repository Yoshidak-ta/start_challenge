from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
  path('schedule/<int:year>/<int:month>', views.schedule, name='schedule'),
  path('schedule_show/<int:year>/<int:month>/<int:day>', views.schedule_show, name='schedule_show'),
  path('schedule/<int:year>/<int:month>/add_todo/', views.add_todo, name='add_todo'),
  path('schedule/<int:year>/<int:month>/complete_todo/<int:todo_id>', views.complete_todo, name='complete_todo'),
  path('schedule/<int:year>/<int:month>/<int:day>/schedule_regist', views.schedule_regist, name='schedule_regist'),
  path('schedule_edit/<int:pk>', views.schedule_edit, name='schedule_edit'),
  path('schedule_delete/<int:pk>', views.schedule_delete, name='schedule_delete'),
  path('schedule_history/<int:pk>', views.get_schedule_history, name='schedule_history'),
  path('objective_regist/', views.objective_regist, name='objective_regist'),
  path('objective_edit/<int:user_id>', views.objective_edit, name='objective_edit'),
  path('objective_goal/<int:pk>', views.objective_goal, name='objective_goal'),
]