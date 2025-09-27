import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

class AutoLogout:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if request.user.is_authenticated:
      now = datetime.datetime.now().timestamp()
      last_activity = request.session.get('last_activity')

      if last_activity and now - last_activity > getattr(settings, "AUTO_LOGOUT_DELAY", 60):
        logout(request)
        messages.error(request, 'セッションが切れました。再度ログインを行ってください。')
        return redirect("/accounts/user_login")
      else:
        request.session['last_activity'] = now
    
    response = self.get_response(request)
    return response