from django.db.models import Sum
import matplotlib.pyplot as plt
import io
import urllib, base64

def encode_img(fig):
  buf = io.BytesIO()
  fig.savefig(buf, format='png')
  buf.seek(0)
  return base64.b64encode(buf.read())

def plot_chart(x, y, limit):
  plt.clf()
  # display month days spaced by 2
  days_int = range(1, max(30, max(x)), 2)
  # plot spending chart
  plt.plot(x, y)
  # plot horizontal line to show savers limit
  plt.hlines(limit, 1, max(30, max(x)), colors='red', linestyles='--')
  plt.xticks(days_int)
  plt.xlabel('Month day')
  plt.ylabel('R$ spent')
  return plt.gcf()

def month_spending_chart(spending_data, monthly_limit):
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
