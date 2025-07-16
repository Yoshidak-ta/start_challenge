from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import os

def portfolio(request):
  return render(request, 'portfolio.html')
