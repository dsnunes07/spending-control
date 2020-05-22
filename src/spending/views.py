from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from django.template import loader
import datetime
from .models import Expense, Saver
from .forms import ExpenseCreate, SaverCreate
from .charts import month_spending_chart
from .data import SpendingData
import math
  
def get_current_saver(request):
  saver_id = request.session.get('saver_id')
  if saver_id is None:
    return HttpResponseRedirect(reverse('spending:login'))
  return Saver.objects.get(id=saver_id)

def current_spending(request):
  saver_id = request.session.get('saver_id')
  if saver_id is None:
    return HttpResponseRedirect(reverse('spending:login'))
  
  current_saver = Saver.objects.get(id=saver_id)
  monthly_limit = float(current_saver.monthly_limit)
  spending_data = SpendingData(current_saver.expense_set.all())
  current_month_spending = spending_data.current_month_spending()
  total_amount, chart = month_spending_chart(current_month_spending, monthly_limit)
  context = {
    'current_month_spending': current_month_spending,
    'chart_html': chart,
    'total_amount': float(total_amount),
    'monthly_limit': float(monthly_limit),
    'limit_percentual': (total_amount/monthly_limit)*100,
    'exceeds_limit': total_amount > monthly_limit
  }
  return render(request, 'spending/current_month_spending.html', context)

def not_current_spending(request, when):
  current_saver = get_current_saver(request)
  data = SpendingData(current_saver.expense_set.all())
  if when == 'past':
    spending_data = data.past_spending()
  else:
    spending_data = data.future_spending()
  context = {
    'spending_data': spending_data,
    'past': when == 'past'
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


