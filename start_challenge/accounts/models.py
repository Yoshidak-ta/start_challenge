from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import (
  AbstractBaseUser, PermissionsMixin
)
from django.utils.timezone import now

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
    user.save(using=self._db)

    return user
  
  def create_superuser(self, username, email, password=None):
    user = self.model(
      username=username,
      email=email,
    )
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user

# ユーザテーブル
class Users(AbstractBaseUser, PermissionsMixin):
  username = models.CharField(max_length=255)
  hurigana = models.CharField(max_length=255, null=False)
  email = models.EmailField(max_length=255, unique=True)
  picture = models.FileField(null=True, upload_to='user_picture/', default='user_picture/no_image.jpeg')
  category = models.ManyToManyField('Categories', blank=True)
  message = models.CharField(max_length=255, null=True)
  password = models.CharField(max_length=255)
  rank = models.IntegerField(default=0)
  objective = models.CharField(max_length=255, null=True, blank=True)
  objective_due_date = models.DateTimeField(null=True, blank=True)
  is_staff = models.BooleanField(default=False)
  last_notificated = models.DateTimeField(null=True, blank=True)
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  def __str__(self):
    return self.email

  class Meta():
    db_table = 'users'

# 得意分野テーブル
class Categories(models.Model):
  categoryname = models.CharField(max_length=55)

  class Meta():
    db_table = 'categories'

  def __str__(self):
    return self.categoryname

