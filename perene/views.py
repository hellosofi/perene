from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, Http404
from django.views import View

from django.shortcuts import render, redirect
from .models import Produto
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    LoginFuncionarioForm, CadastroFuncionarioForm,
    LoginGestorForm, CadastroGestorForm,
)

# def index(request):
#     return HttpResponse("aaaa")

# class MainView(View):
#     def get(self, request):

        
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


class LoginFuncionario(AuthView):
    form_class = LoginFuncionarioForm
    pagina = {
        'tema': 'funcionario',
        'titulo': 'Login de funcionário',
        'descricao': 'Entre com o e-mail e a senha da sua conta para consultar e atualizar o estoque.',
        'botao': 'Entrar',
        'troca_pergunta': 'Ainda não tem conta?',
        'troca_texto': 'Cadastre-se',
        'troca_url': 'cadastro_funcionario',
        'outro_texto': 'Sou gestor',
        'outro_url': 'login_gestor',
    }


class CadastroFuncionario(AuthView):
    form_class = CadastroFuncionarioForm
    pagina = {
        'tema': 'funcionario',
        'titulo': 'Cadastro de funcionário',
        'descricao': 'Crie sua conta com e-mail e senha para acessar o estoque do mercado.',
        'botao': 'Criar conta',
        'troca_pergunta': 'Já tem conta?',
        'troca_texto': 'Entrar',
        'troca_url': 'login_funcionario',
        'outro_texto': 'Sou gestor',
        'outro_url': 'login_gestor',
    }


class LoginGestor(AuthView):
    form_class = LoginGestorForm
    pagina = {
        'tema': 'gestor',
        'titulo': 'Área do gestor',
        'descricao': 'Entre com o mesmo usuário e senha do painel administrativo.',
        'botao': 'Entrar',
        'troca_pergunta': 'Ainda não tem conta de gestor?',
        'troca_texto': 'Cadastre-se',
        'troca_url': 'cadastro_gestor',
        'outro_texto': 'Sou funcionário',
        'outro_url': 'login_funcionario',
    }


class CadastroGestor(AuthView):
    form_class = CadastroGestorForm
    pagina = {
        'tema': 'gestor',
        'titulo': 'Cadastro de gestor',
        'descricao': 'Crie uma conta de gestor. Você vai precisar do código de acesso da administração.',
        'botao': 'Criar conta de gestor',
        'troca_pergunta': 'Já tem conta de gestor?',
        'troca_texto': 'Entrar',
        'troca_url': 'login_gestor',
        'outro_texto': 'Sou funcionário',
        'outro_url': 'login_funcionario',
    }


class Produto_view(LoginRequiredMixin, View):
    def get(self, request):
        try:
            produtos =  Produto.objects.all().order_by('-validade')
        except Produto.DoesNotExist:
            raise Http404("Produto inexistente")
        contexto = {'produto' : produtos}
        return render(request, 'lista_produtos.html', contexto)

class Add_produto(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'inserir_produto.html')

    def post(self, request):
        nome = request.POST.get('nome')
        detalhe = request.POST.get('detalhe')
        validade = request.POST.get('validade')
        
        produto = Produto(nome=nome, detalhe=detalhe, validade=validade)
        produto.save()

        return redirect(reverse('lista_produtos'))    

    # def lista(request):
    #     produtos = Produto.objects.all().order_by('validade')
    #     return render(request, 'lista.html', {'produtos': produtos})

# def add_produto(request):
#     if request.method == 'POST':
#         nome = request.POST.get('nome')
#         detalhe = request.POST.get('detalhe')
#         validade = request.POST.get('validade')

#         if nome:
#             Produto.objects.create(
#                 nome=nome,
#                 detalhe=detalhe,
#                 validade=validade,
#                 # status=Produto.status
#             )
        
#             return redirect('lista_produtos')

    # return render(request, 'form.html')
