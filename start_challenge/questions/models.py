from django.db import models
from accounts.models import Categories, Users
from datetime import datetime
from django.utils.timezone import now

class QuestionCreateManager(models.Manager):

  def question_create(self, title, comment, picture, category, user):
    question = self.update_or_create(
      title=title,
      comment=comment,
      picture=picture,
      category=category,
      user=user,
      updated_at=datetime.now()
    )
    question.save()
    return question

# 質問テーブル
class Questions(models.Model):
  title = models.CharField(max_length=255)
  comment = models.TextField()
  picture = models.FileField(null=True, upload_to='question_picture/', default='question_picture/no_Image.jpg')
  category = models.ManyToManyField(Categories, blank=True)
  user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="questions")
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)

  objects :QuestionCreateManager = QuestionCreateManager()

  class Meta():
    db_table = 'questions'

# 質問構文テンプレートテーブル
class Templates(models.Model):
  title = models.CharField(max_length=255, null=True)
  templatetext = models.TextField()

  class Meta():
    db_table = 'templates'
  
  def field_with_breaks(self):
    return self.templatetext.replace(",", "<br>")
  
#　回答テーブル 
class Answers(models.Model):
  picture = models.FileField(null=True, upload_to='answer_picture/', default='answer_picture/no_Image.jpg')
  comment = models.TextField(null=False)
  user = models.ForeignKey(Users, on_delete=models.CASCADE)
  question = models.ForeignKey(Questions, related_name="answers", on_delete=models.CASCADE)
  created_at = models.DateTimeField(default=now)
  updated_at = models.DateTimeField(default=now)

  class Meta():
    db_table = 'answers'
  
  def __str__(self):
    return f'Answer to:{self.question.title}'