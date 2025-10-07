from datetime import datetime, time, date, timedelta
from django.utils.timezone import localtime, make_aware

class AccessTimeMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
  
  def __call__(self, request):
    request.show_notification = False
    # 通知チェックは認証済みユーザーのみ対象
    if request.user.is_authenticated:
        now = localtime()
        today_9am = datetime.combine(date.today(), time(7, 0))
        reset_time = make_aware(today_9am)

        if request.user.last_notificated == None:
           request.show_notification = True
        elif request.user.last_notificated:
          last_access = request.user.last_notificated + timedelta(hours=9)
          if now >= reset_time and last_access < reset_time:
              request.show_notification = True

    response = self.get_response(request)
    return response