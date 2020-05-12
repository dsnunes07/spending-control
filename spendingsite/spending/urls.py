from django.urls import path
from . import views

app_name = 'spending'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('add/', views.new, name='new'),
    path('create/', views.create, name='create'),
]