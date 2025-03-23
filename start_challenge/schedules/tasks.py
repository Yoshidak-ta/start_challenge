from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Schedules, ToDos
from accounts.utils import send_web_push
from accounts.views import send_push_notification

@shared_task
def check_schedules_and_send_notifications():
    now = timezone.now()

    # スケジュール当日
    today_schedules = Schedules.objects.filter(start_at__date=now.date())
    for schedule in today_schedules:
        send_push_notification('本日の予定', f'スケジュール: {schedule.task}')

    # 開始１時間前
    upcoming_schedules_60 = Schedules.objects.filter(start_at__lte=now + timedelta(hours=1), start_at__gte=now)
    for schedule in upcoming_schedules_60:
        send_push_notification('予定時刻が迫ってます', f'スケジュール：{schedule.task}まであと1時間です。')
    
    # 開始10分前
    upcoming_schedules_10 = Schedules.objects.filter(start_at__lte=now + timedelta(minutes=10), start_at__gte=now)
    for schedule in upcoming_schedules_10:
        send_push_notification('まもなく', f'スケジュール： {schedule.task}まであと10分です')
    
    # Todoタスク未達
    due_todos = ToDos.objects.filter(due_date=now.date(), is_completed=False)
    for todo in due_todos:
        send_push_notification('本日期限のタスクが残っています！', f'タスク: {todo.task}が本日期限です！残りのタスクも達成しましょう！')
    
    