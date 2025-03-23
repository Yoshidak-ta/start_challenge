from django import forms
from accounts.models import Users
from .models import ChatsGroup, Chats

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
    fields = ['groupname', 'picture', 'user']

# チャット投稿フォーム
class ChatRegistForm(forms.ModelForm):
  message = forms.CharField(label='メッセージ')
  picture = forms.FileField(label='画像', required=False)

  class Meta():
    model = Chats
    fields = ('message', 'picture')

  