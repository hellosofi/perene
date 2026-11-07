from django.shortcuts import render

# Create your views here.

from django.db.models import Q, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value
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

    if status_filtro:                                             # MUDOU
        lotes = lotes.filter(produto__status=status_filtro)

    # Contadores do topo da página: continuam contando produtos
    total = Produto.objects.count()
    atencao = Produto.objects.filter(
        status__in=['use_soon', 'low_stock', 'damaged', 'surplus']
    ).count()
    saudaveis = Produto.objects.filter(status='all_good').count()
    pct_saudavel = round(saudaveis / total * 100, 1) if total > 0 else 0

    categorias = (
        Produto.objects
        .exclude(categoria='')
        .values_list('categoria', flat=True)
        .distinct()
        .order_by('categoria')
    )

    produtos_filtro = Produto.objects.order_by('nome')            # NOVO
    produto_selecionado = (                                       # NOVO
        Produto.objects.filter(pk=produto_id).first()
        if produto_id.isdigit() else None
    )

    lista = list(lotes)
    grupos = [                                                    # MUDOU: l = lote
        {
            'titulo': 'Tudo certo',
            'items': [l for l in lista if l.produto.status == 'all_good'],
        },
        {
            'titulo': 'Precisa de atenção',
            'items': [l for l in lista if l.produto.status in ('use_soon', 'low_stock', 'damaged', 'surplus')],
        },
        {
            'titulo': 'Estoque não cadastrado',
            'items': [l for l in lista if l.produto.status == 'undocumented'],
        },
    ]

    return {
        'lotes': lista,                                           # MUDOU: era 'produtos'
        'grupos': grupos,
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
    if request.method == 'POST':
        Produto.objects.create(
            nome=request.POST.get('nome', ''),
            codigo=request.POST.get('codigo', ''),
            categoria=request.POST.get('categoria', ''),
            detalhe=request.POST.get('detalhe', ''),
            unidade=request.POST.get('unidade', ''),
            status=request.POST.get('status', 'all_good'),
        )
        return redirect(reverse('lista_produtos'))

    contexto = contexto_lista(request)
    contexto['mostrar_modal'] = True
    contexto['status_choices'] = Produto.STATUS_CHOICES

    return render(request, 'estoque/lista_produtos.html', contexto)

from django.shortcuts import get_object_or_404
from .forms import LoteForm

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
