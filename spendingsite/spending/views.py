from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from django.template import loader
from django.db.models import Sum
import datetime
from .models import Expense
from .forms import ExpenseCreate
import matplotlib.pyplot as plt
import io
import urllib, base64
import math

def encode_img(fig):
  buf = io.BytesIO()
  fig.savefig(buf, format='png')
  buf.seek(0)
  return base64.b64encode(buf.read())

def plot_chart(x, y):
  plt.clf()
  days_int = range(min(x) + 1, math.ceil(max(x))+1)
  plt.plot(x, y)
  plt.xticks(days_int)
  plt.xlabel('Days')
  plt.ylabel('R$')
  return plt.gcf()

def spending_chart(spending_data):
  sum_by_day = spending_data.values('when__day').annotate(Sum('how_much'))
  total_amount = [0]
  days = [0]
  acc_amount = 0
  for day in sum_by_day:
    days.append(int(day['when__day']))
    total_amount.append(acc_amount + float(day['how_much__sum']))
    acc_amount = total_amount[-1]
  chart_figure = plot_chart(days, total_amount)
  encoded_img = encode_img(chart_figure)
  uri = 'data:image/png;base64,' + urllib.parse.quote(encoded_img)
  html_tag = '<img src = "%s"/>' % uri
  return total_amount[-1], html_tag
  
def index(request):
  current_month_day = timezone.now().day
  current_month_beginning = timezone.now() - datetime.timedelta(days=current_month_day)
  current_month_spending = Expense.objects.filter(when__gte=current_month_beginning).order_by('when')
  total_amount, chart = spending_chart(current_month_spending)
  context = {
    'current_month_spending': current_month_spending,
    'chart_html': chart,
    'total_amount': total_amount
  }
  return render(request, 'spending/spending_table.html', context)

def create(request):
  expense = ExpenseCreate()
  if request.method == 'POST':
    expense = ExpenseCreate(request.POST)
    expense.save()
    return HttpResponseRedirect(reverse('spending:index'))
  else:
    return render(request, 'spending/new.html', {'form_fields': expense})

def update(request, expense_id):
  expense = get_object_or_404(Expense, pk=expense_id)
  expense_form = ExpenseCreate(request.POST or None, instance=expense)
  if expense_form.is_valid():
    expense_form.save()
    return HttpResponseRedirect(reverse('spending:index'))
  return render(request, 'spending/new.html', {'form_fields': expense_form})

def delete(request, expense_id):
  expense = get_object_or_404(Expense, pk=expense_id)
  expense.delete()
  return HttpResponseRedirect(reverse('spending:index'))

