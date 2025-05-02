from django.shortcuts import render
from . import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Questions, Templates, Answers
from datetime import datetime

# 質問投稿
@login_required
def question_regist(request):
  question_regist_form = forms.QuestionRegistForm(request.POST or None, request.FILES or None)
  template = Templates.objects.all()
  if question_regist_form.is_valid():
    try:
      with transaction.atomic():
        question = question_regist_form.save(commit=False)
        question.user = request.user
        question.save()
        question_regist_form.save_m2m()
      messages.info(request, '投稿されました。')
      redirect_url = reverse('accounts:home')
      return redirect(redirect_url)
    except ValidationError as e:
      print(f'エラー：{e}')
      messages.error(request, '入力に誤りがあります。')
  
  return render(
    request, 'questions/question_regist.html', context={
      'question_regist_form':question_regist_form, 'template':template,
    }
  )

# 質問詳細
def question_show(request, pk):
  question = get_object_or_404(Questions, pk=pk)
  answers = question.answers.all()
  if request.method == "POST":
    if not request.user.is_authenticated:
      messages.error(request, '回答するにはログインが必要です。')
      return redirect('accounts:user_login')
    
    question_answer_form = forms.QuestionAnswerForm(request.POST, request.FILES or None)
    if question_answer_form.is_valid():
      answer = question_answer_form.save(commit=False)
      answer.user = request.user
      answer.question = question
      answer.save()

      user = request.user
      answer_count = Answers.objects.filter(user=user).count()
      if answer_count % 3 == 0:
        user.rank += 10
        user.save()
      
      messages.info(request, '回答しました')
      return redirect('questions:question_show', pk=pk)
    else:
      messages.error(request, '回答の入力項目に誤りがございます。')
      return redirect('questions:question_show', pk=pk)

  else:
    question_answer_form = forms.QuestionAnswerForm()
  # answers = question.answers.all()
  # user = request.user
  return render(request, 'questions/question_show.html', context={
    'question':question, 'question_answer_form': question_answer_form, 'answers':answers,
  })

# 質問削除
@login_required
def question_delete(request, pk):
  if request.method == 'POST':
    question = get_object_or_404(Questions, pk=pk)
    question.delete()
    messages.info(request, '質問が削除されました。')
    return redirect('accounts:home')

# 質問編集
@login_required
def question_edit(request, pk):
  question = get_object_or_404(Questions, pk=pk)
  if request.method == "POST":
    question_edit_form = forms.QuestionEditForm(request.POST, request.FILES, instance=question)
    if question_edit_form.is_valid():
      question = question_edit_form.save(commit=False)
      question.updated_at = datetime.now()
      question.save()
      question_edit_form.save_m2m()
      messages.info(request, '質問内容を編集しました。')
      return redirect('questions:question_show', pk=pk)
    else:
      messages.error(request, '編集に失敗しました。もう一度入力事項を確認してください。')
  else:
    question_edit_form = forms.QuestionEditForm(instance=question)
    
  return render(request, 'questions/question_edit.html', context={
    'question':question, 
    'question_edit_form':question_edit_form,
  })
