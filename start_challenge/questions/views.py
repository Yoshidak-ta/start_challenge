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
from django.http import JsonResponse, Http404

# 質問投稿
@login_required
def question_regist(request):
  template = Templates.objects.all()
  question_regist_form = forms.QuestionRegistForm(request.POST or None, request.FILES or None)
  if request.method == 'POST':
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
    else:
      messages.error(request, '質問登録に失敗しました。以下をご確認ください。')
      for field, errors in question_regist_form.errors.items():
        for error in errors:
          messages.error(request, f"{question_regist_form.fields[field].label}:{error}")
    
  return render(
    request, 'questions/question_regist.html', context={
      'question_regist_form':question_regist_form, 'template':template,
    }
  )

# 質問詳細/回答登録
def question_show(request, pk):
  question = get_object_or_404(Questions, pk=pk)
  answers = question.answers.all()
  question_answer_edit_form = forms.QuestionAnswerEditForm()
  if request.method == "POST":
    question_answer_form = forms.QuestionAnswerForm(request.POST, request.FILES or None)
    if question_answer_form.is_valid():
      answer = question_answer_form.save(commit=False)
      answer.user = request.user
      answer.question = question
      answer.save()

      # ランクアップ
      user = request.user
      answer_count = Answers.objects.filter(user=user).count()
      if answer_count % 3 == 0:
        user.rank += 10
        user.save()
      
      messages.info(request, '回答しました')
      return redirect('questions:question_show', pk=pk)
    else:
      messages.error(request, '回答登録に失敗しました。以下をご確認ください。')
      for field, errors in question_answer_form.errors.items():
        for error in errors:
          messages.error(request, f"{question_answer_form.fields[field].label}:{error}")
      return redirect('questions:question_show', pk=pk)

  else:
    question_answer_form = forms.QuestionAnswerForm()
    
  return render(request, 'questions/question_show.html', context={
    'question':question, 'question_answer_form': question_answer_form, 'answers':answers, 'question_answer_edit_form': question_answer_edit_form,
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
      messages.error(request, '質問編集に失敗しました。以下をご確認ください。')
      for field, errors in question_edit_form.errors.items():
        for error in errors:
          messages.error(request, f"{question_edit_form.fields[field].label}:{error}")
  else:
    question_edit_form = forms.QuestionEditForm(instance=question)
    
  return render(request, 'questions/question_edit.html', context={
    'question':question, 
    'question_edit_form':question_edit_form,
  })

# 回答データ取得
def get_answer_data(request, pk):
  try:
    answer = Answers.objects.get(pk=pk)
    return JsonResponse({
      'picture': answer.picture.url if answer.picture else '',
      'comment':answer.comment
    })
  except Answers.DoesNotExist:
    raise Http404('回答がありません')

# 回答編集
def answer_edit(request, pk):
  answer = get_object_or_404(Answers, pk=pk)
  question_id = answer.question.id
  if request.method == 'POST':
    answer_edit_form = forms.QuestionAnswerEditForm(request.POST, request.FILES, instance=answer)
    if answer_edit_form.is_valid():
      answer = answer_edit_form.save(commit=False)
      answer.updated_at = datetime.now()
      answer.save()
      answer_edit_form.save_m2m()
      messages.info(request, '回答が編集されました')
    
    else:
      messages.error(request, '目標編集に失敗しました。以下をご確認ください。')
      for field, errors in answer_edit_form.errors.items():
        for error in errors:
          messages.error(request, f"{answer_edit_form.fields[field].label}:{error}")
      
    return redirect('questions:question_show', question_id)
  
  else:
    answer_edit_form = forms.QuestionAnswerEditForm(instance=answer)
  
  return redirect('questions:question_show', question_id)

# 回答削除
@login_required
def answer_delete(request, pk):
  if request.method == 'POST':
    answer = get_object_or_404(Answers, pk=pk)
    question_id = answer.question.id
    answer.delete()
    messages.info(request, '回答が削除されました。')
  else:
    messages.error(request, '回答の削除に失敗しました')
  
  return redirect('questions:question_show', question_id)
