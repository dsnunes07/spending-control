from django.utils import timezone
import datetime

class SpendingData:
  def __init__(self, spending):
    self.spending = spending
    self.current_month = timezone.now().month
    self.current_year = timezone.now().year

  def current_month_spending(self):
    current_month_spending = self.spending.filter(when__month=self.current_month).filter(when__year=self.current_year).order_by('when')
    return current_month_spending
  
  def past_spending(self):
    today = timezone.now().day
    current_month_beginning = timezone.now() - datetime.timedelta(days=today)
    spending = self.spending.filter(when__lt=current_month_beginning)
    return spending
  
  def future_spending(self):
    spending = self.spending.filter(when__month__gt=self.current_month).filter(when__year__gte=self.current_year)
    return spending

