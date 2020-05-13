from django.urls import path
from . import views

app_name = 'spending'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='new'),
    path('create/', views.create, name='create'),
    path('update/<int:expense_id>', views.update, name='update'),
    path('delete/<int:expense_id>', views.delete, name='delete')
]