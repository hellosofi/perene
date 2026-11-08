from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Funcionario, Tarefa


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'status')


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'responsavel', 'horario', 'concluida')
    list_filter = ('concluida', 'responsavel')