import secrets

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from .decorators import eh_gestor

# perfil
from django.db import transaction
from .models import Mercado, Perfil

User = get_user_model()


# exemplos que aparecem dentro dos campos das telas de entrada
EXEMPLOS = {
    'nome': 'Ex.: Sônia Oliveira',
    'email': 'seuemail@exemplo.com',
    'usuario': 'seuemail@exemplo.com',
    'nome_mercado': 'Ex.: Mercadinho São José',
    'cidade_mercado': 'Ex.: Recife – PE',
    'codigo_mercado': 'Ex.: A1B2C3D4',
}


def campo_senha(label='Senha', autocomplete='current-password', help_text=''):
    return forms.CharField(
        label=label,
        help_text=help_text,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': autocomplete}),
    )


class _ComRequest:
    """Guarda o request (usado pelo authenticate) e o usuário que será logado."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        for nome, campo in self.fields.items():
            if nome in EXEMPLOS:
                campo.widget.attrs.setdefault('placeholder', EXEMPLOS[nome])
        self.user = None

    def finalizar(self):
        """Devolve o usuário que a view vai colocar na sessão."""
        return self.user


# login

class LoginFuncionarioForm(_ComRequest, forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'autofocus': True}),
    )
    senha = campo_senha()

    def clean(self):
        dados = super().clean()
        email, senha = dados.get('email'), dados.get('senha')
        if email and senha:
            alvo = User.objects.filter(email__iexact=email).first()
            user = authenticate(self.request, username=alvo.get_username(), password=senha) if alvo else None
            if user is None:
                raise forms.ValidationError('E-mail ou senha incorretos.')
            if eh_gestor(user):
                raise forms.ValidationError('Esta conta é de gestor. Entre pelo login de gestor.')
            self.user = user
        return dados


class LoginGestorForm(_ComRequest, forms.Form):
    usuario = forms.CharField(
        label='Usuário ou e-mail',
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'autofocus': True}),
    )
    senha = campo_senha()

    def clean(self):
        dados = super().clean()
        usuario, senha = dados.get('usuario'), dados.get('senha')
        if usuario and senha:
            alvo = (User.objects.filter(username=usuario).first()
                    or User.objects.filter(email__iexact=usuario).first())
            user = authenticate(self.request, username=alvo.get_username(), password=senha) if alvo else None
            if user is None:
                raise forms.ValidationError('Usuário ou senha incorretos.')
            if not user.is_staff:
                raise forms.ValidationError('Esta conta não tem acesso de gestor. Entre pelo login de funcionário.')
            self.user = user
        return dados


# cadastro

class _CadastroBase(_ComRequest, forms.Form):
    is_staff = False  # as subclasses definem o tipo de conta

    nome = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'autofocus': True}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    senha = campo_senha('Senha', 'new-password', 'Mínimo de 8 caracteres.')
    confirmar_senha = campo_senha('Confirmar senha', 'new-password')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if (User.objects.filter(email__iexact=email).exists()
                or User.objects.filter(username__iexact=email).exists()):
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean(self):
        dados = super().clean()
        senha, confirmar = dados.get('senha'), dados.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        elif senha and confirmar:
            candidato = User(username=dados.get('email', ''), email=dados.get('email', ''),
                             first_name=dados.get('nome', ''))
            try:
                validate_password(senha, candidato)
            except forms.ValidationError as erro:
                self.add_error('senha', erro)
        return dados

    def finalizar(self):
        d = self.cleaned_data
        # o e-mail também é o username, então "Usuário" no login de gestor aceita o e-mail
        return User.objects.create_user(
            username=d['email'], email=d['email'], password=d['senha'],
            first_name=d['nome'], is_staff=self.is_staff,
        )


class CadastroFuncionarioForm(_CadastroBase):
    is_staff = False
    codigo_mercado = forms.CharField(
        label='Código do mercado',
        max_length=8,
        help_text='Peça este código ao gestor do seu mercado.',
    )

    def clean_codigo_mercado(self):
        codigo = self.cleaned_data['codigo_mercado'].strip().upper()
        mercado = Mercado.objects.filter(codigo_convite=codigo).first()
        if mercado is None:
            raise forms.ValidationError('Código de mercado inválido.')
        self.mercado = mercado
        return codigo

    # cria perfil do funcionário    
    def finalizar(self):
        with transaction.atomic():
            user = super().finalizar()
            Perfil.objects.create(usuario=user, mercado=self.mercado, papel='funcionario')
        return user


class CadastroGestorForm(_CadastroBase):
    is_staff = True
    field_order = ['nome', 'email', 'senha', 'confirmar_senha', 'nome_mercado', 'cidade_mercado', 'codigo']

    codigo = forms.CharField(
        label='Código de acesso',
        help_text='Fornecido pela administração do sistema.',
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    nome_mercado = forms.CharField(label='Nome do mercado', max_length=200)
    cidade_mercado = forms.CharField(label='Cidade', max_length=100, required=False)

    def clean_codigo(self):
        esperado = settings.GESTOR_CODIGO_CONVITE
        if not esperado:
            raise forms.ValidationError('O cadastro de gestor está desativado no momento.')
        informado = self.cleaned_data['codigo']
        if not secrets.compare_digest(informado.encode(), esperado.encode()):
            raise forms.ValidationError('Código de acesso inválido.')
        return informado

    def finalizar(self):
        d = self.cleaned_data
        with transaction.atomic():
            user = super().finalizar()
            mercado = Mercado.objects.create(
                nome=d['nome_mercado'],
                cidade=d['cidade_mercado'],
            )
            Perfil.objects.create(usuario=user, mercado=mercado, papel='gestor')
        return user    
