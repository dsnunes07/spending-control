from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from django.template import loader
import datetime
from .models import Expense, Category
import matplotlib.pyplot as plt
import io
import urllib, base64


class DetailView(generic.DetailView):
  model = Expense
  template_name = 'spending/detail.html'

def encode_img(fig):
  buf = io.BytesIO()
  fig.savefig(buf, format='png')
  buf.seek(0)
  return base64.b64encode(buf.read())

def spending_chart(spending_data):
  total_amount = []
  days = []
  for expense in spending_data:
    days.append(expense.when.day)
    total_amount.append(float(expense.how_much))
  plt.plot(days, total_amount)
  fig = plt.gcf()
  encoded_img = encode_img(fig)
  uri = 'data:image/png;base64,' + urllib.parse.quote(encoded_img)
  html = '<img src = "%s"/>' % uri
  return html
  
def index(request):
  last_30_days = timezone.now() - datetime.timedelta(days=30)
  last_month_spending = Expense.objects.filter(when__gte=last_30_days)
  spending_chart(last_month_spending)

  context = {
    'last_month_spending': last_month_spending,
    'chart_html': spending_chart(last_month_spending)
  }
  return render(request, 'spending/spending_table.html', context)

def new(request):
  context = {'category_list': Category.objects.all()}
  return render(request, 'spending/new.html', context)

def create(request):
  e = Expense(request.POST or None)
  e.save()
  return HttpResponseRedirect(reverse('spending:index'))
