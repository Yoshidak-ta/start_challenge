from django.utils.timezone import now

def current_date_context(request):
  current_date = now()
  return {
    'year': current_date.year,
    'month': current_date.month,
    'day': current_date.day,
  }
