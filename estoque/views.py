from django.shortcuts import render

# Create your views here.

from django.db.models import Q, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from .models import Produto, Lote

def contexto_lista(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    produto_id = request.GET.get('produto', '')                  # NOVO
    status_filtro = request.GET.get('status', '')
    visao = request.GET.get('visao', 'quadro')

    # MUDOU: a lista agora é de lotes, com os que vencem antes primeiro
    lotes = (
        Lote.objects
        .select_related('produto')
        .order_by(F('validade').asc(nulls_last=True))
    )

    if query:                                                     # MUDOU
        lotes = lotes.filter(
            Q(produto__nome__icontains=query) |
            Q(produto__codigo__icontains=query) |
            Q(produto__categoria__icontains=query) |
            Q(local__icontains=query)
        )

    if categoria:                                                 # MUDOU
        lotes = lotes.filter(produto__categoria=categoria)

    if produto_id.isdigit():                                      # NOVO
        lotes = lotes.filter(produto_id=produto_id)

    produtos = list(Produto.objects.prefetch_related('lotes'))
    total = len(produtos)
    atencao = len([p for p in produtos if p.situacao in ('atencao', 'critico')])
    saudaveis = len([p for p in produtos if p.situacao == 'ok'])
    pct_saudavel = round(saudaveis / total * 100, 1) if total > 0 else 0

    categorias = (
        Produto.objects
        .exclude(categoria='')
        .values_list('categoria', flat=True)
        .distinct()
        .order_by('categoria')
    )

    produtos_filtro = Produto.objects.order_by('nome')            
    produto_selecionado = (                                      
        Produto.objects.filter(pk=produto_id).first()
        if produto_id.isdigit() else None
    )

    lista = list(lotes)

    # quantos lotes há em cada situação (antes do filtro de situação)
    contagens = {'todos': len(lista), 'ok': 0, 'atencao': 0, 'critico': 0}
    for l in lista:
        contagens[l.situacao] += 1

    if status_filtro:
        lista = [l for l in lista if l.situacao == status_filtro]

    # colunas do quadro, da mais urgente para a menos urgente
    grupos = [
        {'chave': 'critico', 'titulo': 'Crítico', 'descricao': 'Vencidos ou avariados',
         'items': [l for l in lista if l.situacao == 'critico']},
        {'chave': 'atencao', 'titulo': 'Atenção', 'descricao': 'Vencem logo ou estoque baixo',
         'items': [l for l in lista if l.situacao == 'atencao']},
        {'chave': 'ok', 'titulo': 'Tudo certo', 'descricao': 'Dentro da validade',
         'items': [l for l in lista if l.situacao == 'ok']},
    ]

    return {
        'lotes': lista,                                           # MUDOU: era 'produtos'
        'grupos': grupos,
        'contagens': contagens,
        'total': total,
        'atencao': atencao,
        'pct_saudavel': pct_saudavel,
        'query': query,
        'categoria_atual': categoria,
        'status_atual': status_filtro,
        'visao': visao,
        'categorias': categorias,
        'pagina_atual': 'inventario',
        'produtos_filtro': produtos_filtro,                       # NOVO
        'produto_atual': produto_id,                              # NOVO
        'produto_selecionado': produto_selecionado,               # NOVO
    }
    

@login_required  # requer login
def lista_produtos(request):
    contexto = contexto_lista(request)
    return render(request, 'estoque/lista_produtos.html', contexto)

@login_required  # requer login
def adicionar_produto(request):
    form = ProdutoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_produtos')

    contexto = contexto_lista(request)
    contexto['mostrar_modal'] = True
    contexto['form_produto'] = form

    return render(request, 'estoque/lista_produtos.html', contexto)

from django.shortcuts import get_object_or_404
from .forms import LoteForm, ProdutoForm

@login_required
def adicionar_lote(request, produto_id):
    # TODO: filtrar por mercado (História 9)
    produto = get_object_or_404(Produto, pk=produto_id)
    form = LoteForm(request.POST or None)
    if form.is_valid():
        lote = form.save(commit=False)
        lote.produto = produto
        lote.save()
        return redirect('lista_produtos')
    return render(request, 'estoque/adicionar_lote.html', {'form': form, 'produto': produto})
