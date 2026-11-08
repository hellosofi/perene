from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Count

from perene.decorators import gestor_required
from .forms import TarefaForm
from .models import Funcionario, Tarefa


def contexto_equipe():
    # TODO: filtrar por mercado (História 9)
    funcionarios = Funcionario.objects.annotate(
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__concluida=True)),
    ).prefetch_related('tarefas')

    total_tarefas = Tarefa.objects.count()
    tarefas_concluidas = Tarefa.objects.filter(concluida=True).count()
    pct_conclusao = round(tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    return {
        'funcionarios': funcionarios,
        'pct_conclusao': pct_conclusao,
        'total_tarefas': total_tarefas,
        'tarefas_concluidas': tarefas_concluidas,
        'total_funcionarios': Funcionario.objects.count(),
        'tarefas': Tarefa.objects.select_related('responsavel'),
        'sem_responsavel': Tarefa.objects.filter(responsavel__isnull=True),
        'pagina_atual': 'equipe',
    }


@gestor_required
def equipe(request):
    return render(request, 'funcionarios/equipe.html', contexto_equipe())


@gestor_required
def nova_tarefa(request):
    form = TarefaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Tarefa criada.')
        return redirect('funcionarios')

    contexto = contexto_equipe()
    contexto['form_tarefa'] = form
    return render(request, 'funcionarios/equipe.html', contexto)
