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
            login(request, form.finalizar())
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
