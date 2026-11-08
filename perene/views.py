from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, Http404
from django.views import View

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    LoginFuncionarioForm, CadastroFuncionarioForm,
    LoginGestorForm, CadastroGestorForm,
)
        
def index(request):
  	return render(request, 'index.html') 


class AuthView(View):
    """Base das telas de login e cadastro.

    Valida o formulário, coloca o usuário na sessão e manda para o estoque.
    """
    form_class = None
    template_name = 'auth.html'
    pagina = {}  # textos e links da tela (ver auth.html)

    def render_form(self, request, form):
        return render(request, self.template_name, {**self.pagina, 'form': form})

    def get(self, request):
        return self.render_form(request, self.form_class(request=request))

    def post(self, request):
        form = self.form_class(request.POST, request=request)
        if form.is_valid():
            user = form.finalizar()
            login(request, user)
            # gestor começa pela Visão geral; funcionário, pelo estoque
            perfil = getattr(user, 'perfil', None)
            if perfil is not None and perfil.papel == 'gestor':
                return redirect('visao_geral')
            return redirect('lista_produtos')
        return self.render_form(request, form)


# Textos e links de cada tela de entrada (ver auth.html).
# url_gestor / url_funcionario: para onde levam as opções do seletor de perfil.
SELETOR_LOGIN = {'url_gestor': 'login_gestor', 'url_funcionario': 'login_funcionario'}
SELETOR_CADASTRO = {'url_gestor': 'cadastro_gestor', 'url_funcionario': 'cadastro_funcionario'}


class LoginFuncionario(AuthView):
    form_class = LoginFuncionarioForm
    pagina = {
        **SELETOR_LOGIN,
        'tipo': 'login',
        'tema': 'funcionario',
        'aba': 'Login de funcionário',
        'titulo': 'Que bom ter você aqui',
        'descricao': 'Escolha seu perfil e entre na sua conta.',
        'botao': 'Entrar',
        'troca_pergunta': 'Ainda não tem conta?',
        'troca_texto': 'Criar minha conta',
        'troca_url': 'cadastro_funcionario',
        'painel_frase': 'Seu mercado mais sustentável, um dia de cada vez.',
    }


class CadastroFuncionario(AuthView):
    form_class = CadastroFuncionarioForm
    pagina = {
        **SELETOR_CADASTRO,
        'tipo': 'cadastro',
        'tema': 'funcionario',
        'aba': 'Cadastro de funcionário',
        'titulo': 'Crie sua conta',
        'descricao': 'Leva menos de 1 minuto.',
        'aviso_titulo': 'Você vai precisar do código do mercado',
        'aviso_texto': 'O gestor encontra o código na tela Equipe. Se ainda não recebeu, peça a ele antes de continuar.',
        'botao': 'Criar minha conta',
        'troca_pergunta': 'Já tem conta?',
        'troca_texto': 'Entrar',
        'troca_url': 'login_funcionario',
        'painel_titulo': 'Sua equipe, no mesmo ritmo',
        'painel_texto': 'Você entra no mercado com o código de convite que o gestor compartilha. Sem formulário longo.',
        'painel_passos': [
            ('Peça o código ao gestor', 'São 8 letras e números, como A1B2C3D4.'),
            ('Crie sua conta', 'Nome, e-mail e uma senha.'),
            ('Pronto para o turno', 'Veja suas tarefas e registre lotes.'),
        ],
    }


class LoginGestor(AuthView):
    form_class = LoginGestorForm
    pagina = {
        **SELETOR_LOGIN,
        'tipo': 'login',
        'tema': 'gestor',
        'aba': 'Login de gestor',
        'titulo': 'Que bom ter você aqui',
        'descricao': 'Escolha seu perfil e entre na sua conta.',
        'botao': 'Entrar',
        'troca_pergunta': 'Ainda não tem conta?',
        'troca_texto': 'Cadastrar meu mercado',
        'troca_url': 'cadastro_gestor',
        'painel_frase': 'Seu mercado mais sustentável, um dia de cada vez.',
    }


class CadastroGestor(AuthView):
    form_class = CadastroGestorForm
    pagina = {
        **SELETOR_CADASTRO,
        'tipo': 'cadastro',
        'tema': 'gestor',
        'aba': 'Cadastro de gestor',
        'titulo': 'Crie sua conta',
        'descricao': 'Leva menos de 2 minutos.',
        'botao': 'Criar conta',
        'troca_pergunta': 'Já tem conta?',
        'troca_texto': 'Entrar',
        'troca_url': 'login_gestor',
        'painel_titulo': 'Comece em 2 passos',
        'painel_passos': [
            ('Crie sua conta', 'Seus dados e os do mercado.'),
            ('Convide a equipe', 'Compartilhe o código do mercado.'),
        ],
    }


# ---------------------------------------------------------------------------
# Notificações (tela 09)
# ---------------------------------------------------------------------------

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST

from .decorators import gestor_required
from .models import Notificacao

GRUPOS_NOTIFICACAO = [
    ('estoque', 'Estoque', 'icon-box'),
    ('equipe', 'Equipe', 'icon-users'),
    ('comunicado', 'Comunicados', 'icon-bell'),
]


def notificacoes_visiveis(user):
    """As notificações para todos (sem destinatário) ou só para este usuário."""
    # TODO: filtrar por mercado (História 9)
    return Notificacao.objects.filter(Q(destinatario__isnull=True) | Q(destinatario=user))


@login_required
def notificacoes(request):
    filtro = request.GET.get('categoria', '')
    todas = list(notificacoes_visiveis(request.user).select_related('produto', 'autor'))
    lidas = set(request.user.notificacoes_lidas.values_list('id', flat=True))

    contagens = {'todas': len(todas)}
    grupos = []
    for chave, titulo, icone in GRUPOS_NOTIFICACAO:
        itens = [n for n in todas if n.categoria == chave]
        contagens[chave] = len(itens)
        if itens and filtro in ('', chave):
            grupos.append({'chave': chave, 'titulo': titulo, 'icone': icone, 'itens': itens})

    return render(request, 'notificacoes.html', {
        'grupos': grupos,
        'contagens': contagens,
        'filtro': filtro,
        'lidas': lidas,
        'novas': len([n for n in todas if n.id not in lidas]),
        'publicos': Notificacao.PUBLICO_CHOICES,
        'pagina_atual': 'notificacoes',
    })


@login_required
@require_POST
def marcar_notificacoes_lidas(request):
    for n in notificacoes_visiveis(request.user):
        n.lida_por.add(request.user)
    return redirect('notificacoes')


@gestor_required
@require_POST
def enviar_comunicado(request):
    mensagem = request.POST.get('mensagem', '').strip()
    publico = request.POST.get('publico', 'todos')
    if publico not in dict(Notificacao.PUBLICO_CHOICES):
        publico = 'todos'

    if not mensagem:
        messages.error(request, 'Escreva o comunicado antes de enviar.')
    else:
        nome = request.user.first_name or request.user.username
        Notificacao.objects.create(
            tipo='comunicado',
            titulo=f'Comunicado de {nome}'[:120],
            mensagem=mensagem,
            publico=publico,
            autor=request.user,
        )
        messages.success(request, 'Comunicado enviado para a equipe.')
    return redirect('notificacoes')


# ---------------------------------------------------------------------------
# Visão geral (tela 03)
# ---------------------------------------------------------------------------

from django.utils import timezone

from estoque.models import Lote, Produto
from funcionarios.models import Tarefa


def saudacao():
    hora = timezone.localtime().hour
    if hora < 12:
        return 'Bom dia'
    if hora < 18:
        return 'Boa tarde'
    return 'Boa noite'


@login_required
def visao_geral(request):
    # TODO: filtrar por mercado (História 9)
    agora = timezone.localtime()

    produtos = list(Produto.objects.prefetch_related('lotes'))
    com_lotes = [p for p in produtos if p.situacao != 'sem_lotes']
    em_dia = [p for p in com_lotes if p.situacao == 'ok']
    pct_em_dia = round(len(em_dia) / len(com_lotes) * 100) if com_lotes else 0

    lotes = list(Lote.objects.select_related('produto'))
    criticos = [l for l in lotes if l.situacao == 'critico']
    atencao = [l for l in lotes if l.situacao == 'atencao']
    abaixo_minimo = [p for p in produtos if p.estoque_minimo and p.quantidade_total < p.estoque_minimo]
    registrados_mes = [l for l in lotes
                       if l.criado_em.year == agora.year and l.criado_em.month == agora.month]

    tarefas = list(Tarefa.objects.select_related('responsavel').order_by('horario'))
    pendentes = [t for t in tarefas if not t.concluida]
    # sem campo de data, "atrasada" = horário de hoje já passou e não foi feita
    atrasadas = [t for t in pendentes if t.horario and t.horario < agora.time()]

    prioridades = []
    if criticos:
        prioridades.append({
            'tom': 'critico', 'icone': 'icon-box',
            'titulo': f'{len(criticos)} lote(s) vencido(s) ou avariado(s)',
            'texto': ', '.join(sorted({l.produto.nome for l in criticos})[:3]),
            'acao': 'Ver lotes', 'url': reverse('lista_produtos') + '?status=critico',
        })
    if atencao:
        prioridades.append({
            'tom': 'atencao', 'icone': 'icon-clock',
            'titulo': f'{len(atencao)} lote(s) pedem atenção',
            'texto': 'Vencem logo ou o produto está com estoque baixo.',
            'acao': 'Ver lotes', 'url': reverse('lista_produtos') + '?status=atencao',
        })
    for p in abaixo_minimo[:2]:
        prioridades.append({
            'tom': 'atencao', 'icone': 'icon-box',
            'titulo': f'{p.nome} abaixo do mínimo',
            'texto': f'Restam {p.quantidade_total} {p.unidade or "un."} · mínimo {p.estoque_minimo}',
            'acao': 'Registrar lote', 'url': reverse('adicionar_lote', args=[p.id]),
        })
    if atrasadas:
        prioridades.append({
            'tom': 'equipe', 'icone': 'icon-clock',
            'titulo': f'{len(atrasadas)} tarefa(s) atrasada(s)',
            'texto': 'Passaram do horário e não foram concluídas.',
            'acao': 'Ver tarefas', 'url': reverse('funcionarios'),
        })

    return render(request, 'visao_geral.html', {
        'saudacao': saudacao(),
        'pct_em_dia': pct_em_dia,
        'total_em_dia': len(em_dia),
        'total_com_lotes': len(com_lotes),
        'criticos': len(criticos),
        'atencao': len(atencao),
        'abaixo_minimo': len(abaixo_minimo),
        'registrados_mes': len(registrados_mes),
        'prioridades': prioridades,
        'tarefas_total': len(tarefas),
        'tarefas_feitas': len(tarefas) - len(pendentes),
        'proximas_tarefas': pendentes[:3],
        'pagina_atual': 'visao_geral',
    })
