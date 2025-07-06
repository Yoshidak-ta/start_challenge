from django import forms
from accounts.models import Users
from .models import ChatsGroup, Chats
from django.contrib.auth import get_user_model

# チャットグループ作成フォーム
class ChatsGroupForm(forms.ModelForm):
  groupname = forms.CharField(label='グループ名')
  picture = forms.FileField(label='アイコン画像', required=False)
  user = forms.ModelMultipleChoiceField(
    label='メンバー',
    queryset=Users.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False
  )

  class Meta():
    model = ChatsGroup
    fields = ('groupname', 'picture', 'user')

# チャットグループ編集フォーム
class ChatsGroupEditForm(forms.ModelForm):
  user = forms.ModelMultipleChoiceField(
    queryset=Users.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False
  )

  class Meta():
    model = ChatsGroup
    fields = ('groupname', 'picture', 'user')
    labels = {
      'groupname':'グループ名',
      'picture':'グループアイコン',
    }

# チャット投稿フォーム
class ChatRegistForm(forms.ModelForm):
  message = forms.CharField(label='メッセージ', required=False)
  picture = forms.FileField(label='画像', required=False)

  class Meta():
    model = Chats
    fields = ('message', 'picture')



  