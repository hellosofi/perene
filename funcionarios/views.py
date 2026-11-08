from django.shortcuts import render
from .models import Funcionario, Tarefa
from django.db.models import Q, Count
from perene.decorators import gestor_required 
from perene.utils import mercado_do_usuario

# Create your views here.     
@gestor_required
def equipe(request):
    mercado = mercado_do_usuario(request.user)                                  # 9.4
    funcionarios_do_mercado = Funcionario.objects.filter(mercado=mercado)       # 9.4
    tarefas_do_mercado = Tarefa.objects.filter(mercado=mercado)                 # 9.4

    funcionarios = funcionarios_do_mercado.annotate(                            # 9.4
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__concluida=True)),
    )

    total_tarefas = tarefas_do_mercado.count()                                  # 9.4
    tarefas_concluidas = tarefas_do_mercado.filter(concluida=True).count()      # 9.4
    pct_conclusao = round(tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    total_funcionarios = funcionarios_do_mercado.count()                        # 9.4
    tarefas = tarefas_do_mercado.select_related('responsavel')                  # 9.4

    return render(request, 'funcionarios/equipe.html', {
        'funcionarios': funcionarios,
        'pct_conclusao': pct_conclusao,
        'total_tarefas': total_tarefas,
        'tarefas_concluidas': tarefas_concluidas,
        'total_funcionarios': total_funcionarios,
        'tarefas': tarefas,
        'pagina_atual': 'equipe',
    })
