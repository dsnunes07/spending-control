from django import forms
from .models import Expense

class ExpenseCreate(forms.ModelForm):
  class Meta:
    model = Expense
    fields = '__all__'
