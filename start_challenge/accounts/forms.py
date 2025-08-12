from django import forms
from .models import Users, Categories
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

# 会員登録フォーム
class UserRegistForm(forms.ModelForm):
  username = forms.CharField(label='名前')
  hurigana = forms.CharField(label='ふりがな(ひらがな)')
  email = forms.EmailField(label='メールアドレス')
  picture = forms.FileField(label='アイコン画像', required=False)
  category = forms.ModelMultipleChoiceField(
    label='得意分野',
    queryset=Categories.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False
  )
  message = forms.CharField(label='自己紹介', required=False)
  password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
  confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput())

  class Meta():
    model = Users
    fields = ('username', 'hurigana', 'email', 'picture', 'category', 'message', 'password')
  
  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data['password']
    confirm_password = cleaned_data['confirm_password']
    email = self.cleaned_data['email']
    username = self.cleaned_data['username']
    hurigana = self.cleaned_data['hurigana']
    p = re.compile('[あ-ん]+')
    if password != confirm_password:
      raise self.add_error('パスワードとパスワード再入力の内容が異なります')
    if Users.objects.filter(username=username).exists() and Users.objects.filter(email=email).exists():
      raise forms.ValidationError('このメールアドレスは既に登録されています')
    if not p.fullmatch(hurigana):
      raise forms.ValidationError('ふりがなはひらがなで入力してください')
    
    return cleaned_data
  
  def save(self, commit=False):
    user = super().save(commit=False)
    validate_password(self.cleaned_data['password'], user)
    user.set_password(self.cleaned_data['password'])
    user.save()
    self.save_m2m()
    return user
  
# ログインフォーム
class LoginForm(forms.Form):
  email = forms.CharField(label='メールアドレス', widget=forms.TextInput(attrs={'class': 'form-control'}))
  password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# 会員情報編集フォーム
class UserEditForm(forms.ModelForm):

  class Meta:
    model = Users
    fields = ('username', 'hurigana', 'email', 'picture', 'category', 'message')
    labels = {
      'username':'名前',
      'hurigana':'ふりがな(ひらがな)',
      'email':'メールアドレス',
      'picture':'アイコン画像',
      'category':'得意分野',
      'message':'自己紹介',
    }
    widgets = {
     'category': forms.CheckboxSelectMultiple,
    }
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['picture'].required=False
    self.fields['category'].required=False
    self.fields['message'].required=False

    if self.instance and self.instance.message is None:
      self.initial['message'] = ''

# パスワードリセットフォーム
class PasswordResetForm(forms.Form):
  email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class':'form-control'}))
  password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
  confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput(attrs={'class':'form-control'}))

  def clean(self):
    cleaned_data =  super().clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    email = cleaned_data.get('email')
    # パスワードと再入力の一致確認
    if password != confirm_password:
      self.add_error('password', 'パスワードが一致しません')
    # パスワードのバリデーション
    try:
      validate_password(password)
    except ValidationError as e:
      self.add_error('password', e)
    # メールアドレスの存在確認
    if email and not Users.objects.filter(email=email).exists():
      self.add_error('email', 'このメールアドレスは登録されていません。会員登録をおこなってください。')
    return cleaned_data
  
  def save(self):
    cleaned_data = self.cleaned_data
    email = cleaned_data.get('email')
    password = cleaned_data.get('password')
    user = Users.objects.get(email=email)
    user.set_password(password)
    user.save()
    return user

# パスワード変更
class ChangePasswordForm(forms.Form):
  password = forms.CharField(label='現在のパスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
  new_password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
  confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput(attrs={'class':'form-control'}))

  def __init__(self, *args, user=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.user = user
  
  def clean_current_password(self):
    password = self.cleaned_data.get('password')
    if not self.user.check_password(password):
      raise forms.ValidationError('現在のパスワードが間違っています')
    return password

  def clean(self):
    cleaned_data =  super().clean()
    new_password = cleaned_data.get('new_password')
    confirm_password = cleaned_data.get('confirm_password')
    # 新しいパスワードと再入力の一致確認
    if new_password != confirm_password:
      self.add_error('new_password', 'パスワードが一致しません')
    # 新しいパスワードのバリデーション
    try:
      validate_password(new_password)
    except ValidationError as e:
      self.add_error('new_password', e)
    return cleaned_data
  
  def save(self):
    cleaned_data = self.cleaned_data
    new_password = cleaned_data.get('new_password')
    user = self.user
    user.set_password(new_password)
    user.save()
    return user

# 目標設定フォーム
class ObjectiveRegistForm(forms.ModelForm):
  objective = forms.CharField(label='目標')
  objective_due_date = forms.DateTimeField(label='期限')

  class Meta:
    model = Users
    fields = ('objective', 'objective_due_date')

# 目標編集フォーム
class ObjectiveEditForm(forms.ModelForm):

  class Meta:
    model = Users
    fields = ('objective', 'objective_due_date')
    labels = {
      'objective':'目標',
      'objective_due_date':'期限',
    }
  
  def clean(self):
    cleaned_data = super().clean()
    objective = cleaned_data.get('objective')
    due_date = cleaned_data.get('objective_due_date')
    if not objective:
      self.add_error('objective', '必須項目です')
    if not due_date:
      self.add_error('objective_due_date', '必須項目です')
    return cleaned_data

# ユーザ検索フォーム
class UsersSearchForm(forms.Form):
  query = forms.CharField(
    label='検索',
    max_length=200,
    required=False,
    widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'ユーザを検索'})
  )
  category = forms.ModelChoiceField(
    label='カテゴリ',
    queryset=Categories.objects.all(),
    required=False,
    empty_label='得意分野を選択▼',
    widget=forms.Select(attrs={'class':'form-control'})
  )

# 質問検索フォーム
class QuestionsSearchForm(forms.Form):
  query = forms.CharField(
    label='検索',
    max_length=200,
    required=False,
    widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'質問を検索'})
  )
  category = forms.ModelChoiceField(
    label='カテゴリ',
    queryset=Categories.objects.all(),
    required=False,
    empty_label='カテゴリを選択▼',
    widget=forms.Select(attrs={'class':'form-control'})
  )

# 検索エンジン
class SearchForm(forms.Form):
  query = forms.CharField(
    label='検索',
    max_length=200,
    required=False,
    widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'ユーザを検索'})
  )