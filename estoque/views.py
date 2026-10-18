from django.shortcuts import render

# Create your views here.

from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Produto

def contexto_lista(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    status_filtro = request.GET.get('status', '')
    visao = request.GET.get('visao', 'quadro')

    produtos = Produto.objects.all()

    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query) |
            Q(codigo__icontains=query) |
            Q(categoria__icontains=query)
        )

    if categoria:
        produtos = produtos.filter(categoria=categoria)

    if status_filtro:
        produtos = produtos.filter(status=status_filtro)

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

    lista = list(produtos)
    grupos = [
        {
            'titulo': 'Tudo certo',
            'items': [p for p in lista if p.status == 'all_good'],
        },
        {
            'titulo': 'Precisa de atenção',
            'items': [p for p in lista if p.status in ('use_soon', 'low_stock', 'damaged', 'surplus')],
        },
        {
            'titulo': 'Estoque não cadastrado',
            'items': [p for p in lista if p.status == 'undocumented'],
        },
    ]

    return {
        'produtos': lista,
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
    }
    

def lista_produtos(request):
    contexto = contexto_lista(request)
    return render(request, 'estoque/lista_produtos.html', contexto)

def adicionar_produto(request):
    if request.method == 'POST':
        Produto.objects.create(
            nome=request.POST.get('nome', ''),
            codigo=request.POST.get('codigo', ''),
            categoria=request.POST.get('categoria', ''),
            detalhe=request.POST.get('detalhe', ''),
            quantidade=request.POST.get('quantidade', 0),
            unidade=request.POST.get('unidade', ''),
            validade=request.POST.get('validade') or None,
            status=request.POST.get('status', 'all_good'),
        )
        return redirect(reverse('lista_produtos'))

    contexto = contexto_lista(request)
    contexto['mostrar_modal'] = True
    contexto['status_choices'] = Produto.STATUS_CHOICES

    return render(request, 'estoque/lista_produtos.html', contexto)

