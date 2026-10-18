from django.shortcuts import render
from .models import Funcionario, Tarefa
from django.db.models import Q, Count

# Create your views here.

def equipe(request):
    funcionarios = Funcionario.objects.annotate(
        total_tarefas = Count('tarefas'),
        tarefas_concluidas = Count('tarefas', filter=Q(tarefas__concluida = True)) 
    )

    total_tarefas = Tarefa.objects.count()
    tarefas_concluidas = Tarefa.objects.filter(concluida = True).count()

    pct_conclusao = round(tarefas_concluidas/ total_tarefas * 100) if total_tarefas > 0 else 0

    total_funcionarios = Funcionario.objects.count()
    tarefas = Tarefa.objects.select_related('responsavel')

    return render(request, "funcionarios/equipe.html",
                  {
                    'funcionarios': funcionarios,
                    'pct_conclusao': pct_conclusao,
                    'total_tarefas': total_tarefas,
                    'tarefas_concluidas': tarefas_concluidas,
                    'total_funcionarios': total_funcionarios,
                    'tarefas': tarefas, 
                    'pagina_atual': 'equipe'
                }
                  
    )
