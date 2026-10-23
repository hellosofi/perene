from django.urls import path
from . import views

urlpatterns = [
    path('funcionarios/', views.equipe, name='funcionarios'),
    ]
