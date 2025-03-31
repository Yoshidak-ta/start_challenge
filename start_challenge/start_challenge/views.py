from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import os

def portfolio(request):
  return render(request, 'portfolio.html')

def service_worker(request):
  sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
  if os.path.exists(sw_path):
    with open(sw_path, 'r', encoding='utf-8') as f:
      response = HttpResponse(f.read(), content_type='application/javascript')
      response['Service-Worker-Allowed'] = '/'
      return response
  return HttpResponse('Service Worker not found', status=404)