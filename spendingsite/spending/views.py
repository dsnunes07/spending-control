from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from django.template import loader
from django.db.models import Sum
import datetime
from .models import Expense, Saver
from .forms import ExpenseCreate, SaverCreate
import matplotlib.pyplot as plt
import io
import urllib, base64
import math

def encode_img(fig):
  buf = io.BytesIO()
  fig.savefig(buf, format='png')
  buf.seek(0)
  return base64.b64encode(buf.read())

def plot_chart(x, y, limit):
  plt.clf()
  # display month days spaced by 5
  days_int = range(1, max(30, max(x)), 2)
  # plot spending chart
  plt.plot(x, y)
  # plot horizontal line to show savers limit
  plt.hlines(limit, 1, max(30, max(x)), colors='red', linestyles='--')
  plt.xticks(days_int)
  plt.xlabel('Month day')
  plt.ylabel('R$')
  return plt.gcf()

def spending_chart(spending_data, monthly_limit):
  sum_by_day = spending_data.values('when__day').annotate(Sum('how_much'))
  total_amount = [0]
  days = [0]
  acc_amount = 0
  for day in sum_by_day:
    days.append(int(day['when__day']))
    total_amount.append(acc_amount + float(day['how_much__sum']))
    acc_amount = total_amount[-1]
  chart_figure = plot_chart(days, total_amount, monthly_limit)
  encoded_img = encode_img(chart_figure)
  uri = 'data:image/png;base64,' + urllib.parse.quote(encoded_img)
  html_tag = '<img src = "%s"/>' % uri
  return total_amount[-1], html_tag
  
def index(request):
  saver_id = request.session.get('saver_id')
  if saver_id is None:
    return login(request)
  current_saver = Saver.objects.get(id=saver_id)
  monthly_limit = float(current_saver.monthly_limit)
  current_month_day = timezone.now().day
  current_month_beginning = timezone.now() - datetime.timedelta(days=current_month_day)
  current_month_spending = current_saver.expense_set.filter(when__gte=current_month_beginning).order_by('when')
  total_amount, chart = spending_chart(current_month_spending, monthly_limit)
  context = {
    'current_month_spending': current_month_spending,
    'chart_html': chart,
    'total_amount': float(total_amount),
    'monthly_limit': float(monthly_limit),
    'limit_percentual': (total_amount/monthly_limit)*100,
    'exceeds_limit': total_amount > monthly_limit
  }
  return render(request, 'spending/spending_table.html', context)

def create(request):
  expense = ExpenseCreate()
  if request.method == 'POST':
    expense_form = ExpenseCreate(request.POST)
    expense = expense_form.save(commit=False)
    expense.saver = Saver.objects.get(id=request.session.get('saver_id'))
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

def sessions(request):
  return HttpResponse(request.session.get('current_limit'))

def login(request):
  return render(request, 'spending/login.html')

def create_saver(request):
  new_saver = SaverCreate()
  if request.method == 'POST':
    saver = SaverCreate(request.POST)
    saver.save()
    return authenticate(request)
  else:
    return render(request, 'spending/register.html', {'form_fields': new_saver})

def update_saver(request, saver_id):
  saver = get_object_or_404(Saver, pk=saver_id)
  saver_form = SaverCreate(request.POST or None, instance=saver)
  if saver_form.is_valid():
    saver_form.save()
    return HttpResponseRedirect(reverse('spending:index'))
  return render(request, 'spending/register.html', {'form_fields': saver_form})

def authenticate(request):
  try:
    saver = Saver.objects.get(username=request.POST['username'])
  except Saver.DoesNotExist:
    return render(request, 'spending/error_page.html', {'error_message': 'User not found. Check your information'})

  if saver.password == request.POST['password']:
    request.session['saver_id'] = int(saver.id)
    request.session['saver_name'] = saver.name
    request.session['saver_limit'] = float(saver.monthly_limit)
    return HttpResponseRedirect(reverse('spending:index'))
  else:
    saver = None
    return render(request, 'spending/error_page.html', {'error_message': 'Invalid username or password'})

def logout(request):
  request.session.flush()
  return login(request)


