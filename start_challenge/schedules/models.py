from django.db import models
from django.utils.timezone import now
from django.conf import settings

# スケジュールテーブル
class Schedules(models.Model):
  start_at = models.DateTimeField()
  end_at = models.DateTimeField()
  task = models.CharField(max_length=255)
  place = models.CharField(max_length=255, null=True)
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)
  user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="schedules")

  def start_date(self):
    return self.start_at.strftime('%Y-%m-%d')
  
  def end_date(self):
    return self.end_at.strftime('%Y-%m-%d')

  class Meta():
    db_table = 'schedules'

# スケジュール更新履歴テーブル
class SchedulesHistory(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  schedule = models.ForeignKey(Schedules, on_delete=models.CASCADE)
  updated_at = models.DateTimeField(default=now)

  class Meta():
    db_table = 'schedules_history'
  
# ToDoリストテーブル
class ToDos(models.Model):
  PRIORITY_CHOICES = [
    (1, '重'), (2, '中'), (3, '低'),
  ]
  task = models.CharField(max_length=255)
  priority = models.IntegerField(
    choices=PRIORITY_CHOICES,
    verbose_name='優先度',
    default=2
  )
  due_date = models.DateField()
  is_completed = models.BooleanField(default=False)
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

  class Meta():
    db_table = 'todos'

