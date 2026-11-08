from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Count

from perene.decorators import gestor_required
from perene.utils import mercado_do_usuario
from .forms import TarefaForm
from .models import Funcionario, Tarefa


def contexto_equipe(mercado):
    funcionarios_do_mercado = Funcionario.objects.filter(mercado=mercado)       # 9.4
    tarefas_do_mercado = Tarefa.objects.filter(mercado=mercado)                 # 9.4

    funcionarios = funcionarios_do_mercado.annotate(
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__concluida=True)),
    ).prefetch_related('tarefas')

    total_tarefas = tarefas_do_mercado.count()
    tarefas_concluidas = tarefas_do_mercado.filter(concluida=True).count()
    pct_conclusao = round(tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    return {
        'funcionarios': funcionarios,
        'pct_conclusao': pct_conclusao,
        'total_tarefas': total_tarefas,
        'tarefas_concluidas': tarefas_concluidas,
        'total_funcionarios': funcionarios_do_mercado.count(),
        'tarefas': tarefas_do_mercado.select_related('responsavel'),
        'sem_responsavel': tarefas_do_mercado.filter(responsavel__isnull=True),
        'pagina_atual': 'equipe',
    }


@gestor_required
def equipe(request):
    mercado = mercado_do_usuario(request.user)
    return render(request, 'funcionarios/equipe.html', contexto_equipe(mercado))


@gestor_required
def nova_tarefa(request):
    mercado = mercado_do_usuario(request.user)
    form = TarefaForm(request.POST or None)
    # só dá para escolher como responsável alguém do mesmo mercado
    form.fields['responsavel'].queryset = Funcionario.objects.filter(mercado=mercado)

    if form.is_valid():
        tarefa = form.save(commit=False)
        tarefa.mercado = mercado                                                # 9.5
        tarefa.save()
        messages.success(request, 'Tarefa criada.')
        return redirect('funcionarios')

    contexto = contexto_equipe(mercado)
    contexto['form_tarefa'] = form
    return render(request, 'funcionarios/equipe.html', contexto)
