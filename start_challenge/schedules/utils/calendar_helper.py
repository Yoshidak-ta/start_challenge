import calendar
from datetime import datetime, timedelta

class CalendarHelper:
  def __init__(self, year=None, month=None, day=None):
    self.year = year or datetime.now().year
    self.month = month or datetime.now().month
    self.day = day or datetime.now().day

  def generate_month_calendar(self):
    calendar.setfirstweekday(calendar.SUNDAY)
    month_calendar = calendar.monthcalendar(self.year, self.month)
    return month_calendar
  
  def get_month_days(self):
    first_day = datetime(self.year, self.month, self.day)
    last_day = datetime(self.year, self.month, self.day)
    # last_day = datetime(self.year, self.month, calendar.monthrange(self.year, self.month)[1], 23, 59, 59, 999999)
    
    return (first_day, last_day)