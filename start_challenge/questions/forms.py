from django import forms
from accounts.models import Categories
from .models import Questions, Answers

# 質問登録フォーム
class QuestionRegistForm(forms.ModelForm):
  title = forms.CharField(label='タイトル')
  picture = forms.FileField(label='画像', required=False)
  category = forms.ModelMultipleChoiceField(
    label='分野',
    queryset=Categories.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=True,
  )
  comment = forms.CharField(label='質問内容')

  class Meta():
    model = Questions
    fields = ('title', 'picture', 'category', 'comment')

# 回答投稿フォーム
class QuestionAnswerForm(forms.ModelForm):
  picture = forms.FileField(label='画像', required=False)
  comment = forms.CharField(label='回答')
  
  class Meta():
    model = Answers
    fields = ('picture', 'comment')

# 質問編集フォーム
class QuestionEditForm(forms.ModelForm):

  class Meta:
    model = Questions
    fields = ('title', 'picture', 'category', 'comment')
    labels = {
      'title':'タイトル',
      'picture':'画像',
      'category':'分野',
      'comment':'質問内容',
    }
    widgets = {
      'category': forms.CheckboxSelectMultiple,
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['picture'].required=False
    self.fields['category'].required=False


