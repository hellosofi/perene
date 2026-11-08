from django.shortcuts import render

# Create your views here.

from django.db.models import Q, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.utils import timezone
from .models import Produto, Lote
from perene.utils import mercado_do_usuario

def contexto_lista(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    produto_id = request.GET.get('produto', '')
    status_filtro = request.GET.get('status', '')
    visao = request.GET.get('visao', 'quadro')

    mercado = mercado_do_usuario(request.user)                          # 9.4
    produtos_do_mercado = Produto.objects.filter(mercado=mercado)       # 9.4

    lotes = (
        Lote.objects
        .filter(produto__mercado=mercado)                               # 9.4
        .select_related('produto')
        .order_by(F('validade').asc(nulls_last=True))
    )

    if query:
        lotes = lotes.filter(
            Q(produto__nome__icontains=query) |
            Q(produto__codigo__icontains=query) |
            Q(produto__categoria__icontains=query) |
            Q(local__icontains=query)
        )

    if categoria:
        lotes = lotes.filter(produto__categoria=categoria)

    if produto_id.isdigit():
        lotes = lotes.filter(produto_id=produto_id)

    produtos = list(produtos_do_mercado.prefetch_related('lotes'))     # 9.4
    total = len(produtos)
    atencao = len([p for p in produtos if p.situacao in ('atencao', 'critico')])
    saudaveis = len([p for p in produtos if p.situacao == 'ok'])
    pct_saudavel = round(saudaveis / total * 100, 1) if total > 0 else 0

    categorias = (
        produtos_do_mercado                                             # 9.4
        .exclude(categoria='')
        .values_list('categoria', flat=True)
        .distinct()
        .order_by('categoria')
    )

    produtos_filtro = produtos_do_mercado.order_by('nome')             # 9.4
    produto_selecionado = (
        produtos_do_mercado.filter(pk=produto_id).first()              # 9.4
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
        'lotes': lista,
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
        'produtos_filtro': produtos_filtro,
        'produto_atual': produto_id,
        'produto_selecionado': produto_selecionado,
    }
    

@login_required  # requer login
def lista_produtos(request):
    contexto = contexto_lista(request)
    return render(request, 'estoque/lista_produtos.html', contexto)

@login_required
def adicionar_produto(request):
    form = ProdutoForm(request.POST or None)
    if form.is_valid():
        produto = form.save(commit=False)                        # 9.5 (era: form.save())
        produto.mercado = mercado_do_usuario(request.user)       # 9.5
        produto.save()                                           # 9.5
        return redirect('lista_produtos')

    contexto = contexto_lista(request)
    contexto['mostrar_modal'] = True
    contexto['form_produto'] = form

    return render(request, 'estoque/lista_produtos.html', contexto)

from django.shortcuts import get_object_or_404
from .forms import LoteForm, ProdutoForm

@login_required
def adicionar_lote(request, produto_id):
    produto = get_object_or_404(                                 # 9.6
        Produto, pk=produto_id, mercado=mercado_do_usuario(request.user)
    )
    form = LoteForm(request.POST or None)
    if form.is_valid():
        lote = form.save(commit=False)
        lote.produto = produto
        lote.save()
        return redirect('lista_produtos')
    return render(request, 'estoque/adicionar_lote.html', {'form': form, 'produto': produto})


@login_required
def detalhe_produto(request, produto_id):
    produto = get_object_or_404(                                 # 9.6
        Produto, pk=produto_id, mercado=mercado_do_usuario(request.user)
    )
    lotes = list(produto.lotes.order_by(F('validade').asc(nulls_last=True)))

    # próximo vencimento: o lote com a validade mais próxima que ainda não venceu
    hoje = timezone.localdate()
    a_vencer = [l for l in lotes if l.validade and l.validade >= hoje and not l.avariado]
    avariados = [l for l in lotes if l.avariado]

    return render(request, 'estoque/detalhe_produto.html', {
        'produto': produto,
        'lotes': lotes,
        'total': sum(l.quantidade for l in lotes),
        'proximo': a_vencer[0] if a_vencer else None,
        'avariados': avariados,
        'pagina_atual': 'inventario',
    })
