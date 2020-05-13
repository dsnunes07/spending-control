from django import forms
from .models import Expense, Saver

class ExpenseCreate(forms.ModelForm):
  class Meta:
    model = Expense
    exclude = ['saver']
  
class SaverCreate(forms.ModelForm):
  class Meta:
    model = Saver
    fields = ['name', 'username', 'password', 'monthly_limit']
    widgets = {
      'password': forms.PasswordInput(render_value=True)
    }
