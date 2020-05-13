from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def brazilian_currency(amount):
  if amount:
    amount = round(float(amount), 2)
    return "R$ %s,%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-2:])
  return " R$ 0,00"

@register.filter
def two_decimal_places(amount):
  return round(float(amount), 2)