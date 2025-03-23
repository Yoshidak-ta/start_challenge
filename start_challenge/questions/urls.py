from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
  path('question_regist', views.question_regist, name='question_regist'),
  path('question/<int:pk>', views.question_show, name='question_show'),
  path('question_delete/<int:pk>', views.question_delete, name='question_delete'),
  path('question_edit/<int:pk>', views.question_edit, name='question_edit'),
]