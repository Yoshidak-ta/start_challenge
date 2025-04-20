from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import (
  AbstractBaseUser, PermissionsMixin
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuid import uuid4
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
import uuid
from django.utils.timezone import now
from django.core.mail import send_mail
from django.db.models.signals import post_save

class UserManager(BaseUserManager):

  def create_user(self, username, email, picture, category, message, password=None, **extra_fields):
    if not email:
      raise ValueError('メールアドレスが存在しません')
    
    user = self.model(
      username=username,
      email=self.normalize_email(email),
      picture=picture,
      category=category,
      message=message,
      **extra_fields
    )
    user.set_password(password)
    # user.is_active = True
    user.save(using=self._db)

    return user
  
  def create_superuser(self, username, email, password=None):
    user = self.model(
      username=username,
      email=email,
    )
    user.set_password(password)
    user.is_staff = True
    user.is_active = True
    user.is_superuser = True
    user.save(using=self._db)

    return user

# ユーザテーブル
class Users(AbstractBaseUser, PermissionsMixin):
  username = models.CharField(max_length=255)
  email = models.EmailField(max_length=255, unique=True)
  picture = models.FileField(null=True, upload_to='user_picture/', default='user_picture/no_image.jpeg')
  category = models.ManyToManyField('Categories', blank=True)
  message = models.CharField(max_length=255, null=True)
  password = models.CharField(max_length=255)
  rank = models.IntegerField(default=0)
  objective = models.CharField(max_length=255, null=True, blank=True)
  objective_due_date = models.DateTimeField(null=True, blank=True)
  is_active = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  def __str__(self):
    return self.email

  class Meta():
    db_table = 'users'


class UserActivateTokensManager(models.Manager):

  def activate_user_by_token(self, token):
    user_activate_token = self.filter(
      token = token,
      expired_at__gte = datetime.now()
    ).first()

    if hasattr(user_activate_token, 'user'):
      user = user_activate_token.user
      user.is_active = True
      user.save()
      return user
  
  def create_or_update_token(self, user):
    token = str(uuid4())
     # トークンの有効期限
    expired_at = timezone.now() + timedelta(days=1)
    user_token, created = self.update_or_create(
      user=user,
      defaults={'token':token, 'expired_at':expired_at,}
    )
    return user_token

# 各ユーザに発行するアカウント有効化に必要なトークンを保存するテーブル
class UserActivateTokens(models.Model):
  token = models.UUIDField(default=uuid.uuid4)
  expired_at = models.DateTimeField()
  user = models.OneToOneField(
    'Users', on_delete=models.CASCADE,
    related_name='user_activate_token'
  )
  
  objects :UserActivateTokensManager = UserActivateTokensManager()

  class Meta:
    db_table = 'user_activate_token'

# 発行したトークンをメールにて送信→有効化
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def publish_token(sender, created, instance, **kwargs): 
  if created:
    if not instance.is_active:
      user_active_token = UserActivateTokens.objects.create(
        user=instance,
        expired_at=datetime.now()+timedelta(days=settings.ACTIVATION_EXPIRED_DAYS),
      )
      subject = 'Please Activate Your Account'
      message = f'URLにアクセスしてユーザを有効化にしましょう！\n http://127.0.0.1:8000/accounts/users/{user_active_token.token}'
    if instance.is_active:
      subject = 'Activated! Your Accounts!'
      message = 'ユーザが使用できるようになりました！'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [
      instance.email,
    ]
    send_mail(subject, message, from_email, recipient_list)

# 得意分野テーブル
class Categories(models.Model):
  categoryname = models.CharField(max_length=55)

  class Meta():
    db_table = 'categories'

  def __str__(self):
    return self.categoryname


# Webプッシュ通知管理テーブル
class WebPushSubscription(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
  endpoint = models.TextField(unique=True)
  p256dh_key = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta():
    db_table = 'webpush_subscription'

  def __str__(self):
    return self.endpoint
