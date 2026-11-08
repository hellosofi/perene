from django.urls import path
from . import views

urlpatterns = [
    path('funcionarios/', views.equipe, name='funcionarios'),
    path('funcionarios/tarefas/nova/', views.nova_tarefa, name='nova_tarefa'),
]
