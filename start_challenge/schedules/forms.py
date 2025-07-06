from django import forms
from .models import ToDos, Schedules
from accounts.models import Users
from django.contrib.auth import get_user_model

# ToDoリストタスク追加フォーム
class ToDoListForm(forms.ModelForm):
  task = forms.CharField(label='タスク')
  due_date = forms.DateField(
    label='期限',
    widget=forms.DateInput(
      attrs={'type':'date', 'class':'form-control', 'name':'date'}
    )
  )
  priority = forms.ChoiceField(
    label='優先度',
    choices=((1, '高'), (2, '中'), (3, '低')),
    widget=forms.RadioSelect
  )

  class Meta():
    model = ToDos
    fields = ['task', 'due_date', 'priority']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.instance and self.instance.pk:
      self.fields['due_date'].initial = self.instance.due_date.strftime('%Y-%m-%d')

# スケジュール登録フォーム
class ScheduleRegistForm(forms.ModelForm):
  start_at = forms.DateTimeField(
    label='開始',
    widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),  
  )
  end_at = forms.DateTimeField(
    label='終了',
    widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),  
  )
  task = forms.CharField(label='内容')
  place = forms.CharField(label='場所', required=False)
  user = forms.ModelMultipleChoiceField(
    label='登録ユーザ',
    queryset=Users.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False
  )

  class Meta():
    model = Schedules
    fields = ['start_at', 'end_at', 'task', 'place', 'user']

  def clean(self):
    cleaned_data = super().clean()
    user = cleaned_data.get('user')
    if not user:
      self.add_error('user', 'ユーザーを選択してください')
    return cleaned_data

# スケジュール編集フォーム
class ScheduleEditForm(forms.ModelForm):
  user = forms.ModelMultipleChoiceField(
    queryset=get_user_model().objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False
  )

  class Meta():
    model = Schedules
    fields = ['start_at', 'end_at', 'task', 'place', 'user']
    labels = {
      'start_at':'開始',
      'end_at':'終了',
      'task':'内容',
      'place':'場所',
    }


