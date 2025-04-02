from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('todos/', views.todos, name='todos')
]
