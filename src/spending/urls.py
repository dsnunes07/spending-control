from django.urls import path
from . import views

app_name = 'spending'
urlpatterns = [
    path('', views.index, name='index'),
    path('expense/add/', views.create, name='new_expense'),
    path('expense/create/', views.create, name='create_expense'),
    path('expense/<int:expense_id>/update/', views.update, name='update_expense'),
    path('expense/<int:expense_id>/delete/', views.delete, name='delete_expense'),
    path('sessions', views.sessions, name='sessions'),
    path('login', views.login, name='login'),
    path('saver/create', views.create_saver, name='register_saver'),
    path('saver/<int:saver_id>/update', views.update_saver, name='update_saver'),
    path('authenticate', views.authenticate, name='auth'),
    path('logout', views.logout, name='logout')
]