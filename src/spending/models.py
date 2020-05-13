from django.db import models
from django.forms import ModelForm
from django.utils import timezone
import datetime

class Saver(models.Model):
  name = models.CharField(max_length=200)
  username = models.CharField(max_length=20, unique=True, null=False, blank=False)
  password = models.CharField(max_length=100, null=False)
  monthly_limit = models.DecimalField(max_digits=8, decimal_places=2)

class Expense(models.Model):
  description = models.CharField(max_length=200)
  how_much = models.DecimalField(max_digits=8, decimal_places=2)
  when = models.DateField(default=timezone.now())
  saver = models.ForeignKey(Saver, on_delete=models.CASCADE, default=1)



