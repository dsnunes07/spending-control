from django.db import models
from django.forms import ModelForm
from django.utils import timezone
import datetime

class Expense(models.Model):
  description = models.CharField(max_length=200)
  how_much = models.DecimalField(max_digits=8, decimal_places=2)
  when = models.DateField(default=timezone.now())



