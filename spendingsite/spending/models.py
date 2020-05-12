from django.db import models

class Category(models.Model):
  description = models.CharField(max_length=200)

class Expense(models.Model):
  description = models.CharField(max_length=200)
  how_much = models.DecimalField(max_digits=8, decimal_places=2)
  when = models.DateTimeField('spense_date')
  category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

