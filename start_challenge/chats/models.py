from django.db import models
from accounts.models import Users
from django.utils.timezone import now

# チャットグループテーブル
class ChatsGroup(models.Model):
  CATEGORY_CHOICES = [
    (1, '共有チャット'),
    (2, 'グループチャット'),
    (3, '個人チャット'),
  ]

  group_category = models.IntegerField(choices=CATEGORY_CHOICES)
  groupname = models.CharField(max_length=50, null=True)
  picture = models.FileField(null=True, upload_to='group_picture/', default='group_picture/no_image.jpeg')
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)
  user = models.ManyToManyField(Users, related_name='chat_group')

  class Meta:
    db_table = 'chats_group'

# チャットテーブル
class Chats(models.Model):
  message = models.TextField()
  picture = models.FileField(null=True, upload_to='chats_picture/')
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)
  user = models.ForeignKey(
    Users, on_delete=models.CASCADE, null=True, related_name='chats'
  )
  chatsgroup = models.ForeignKey(
    ChatsGroup, on_delete=models.CASCADE, related_name='chats'
  )

  class Meta:
    db_table = 'chats'
