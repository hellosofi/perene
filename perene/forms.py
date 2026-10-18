import secrets

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


def campo_senha(label='Senha', autocomplete='current-password'):
    return forms.CharField(
        label=label,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': autocomplete}),
    )


class _ComRequest:
    """Guarda o request (usado pelo authenticate) e o usuário que será logado."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
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
            if user.is_staff:
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
    senha = campo_senha('Senha', 'new-password')
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


class CadastroGestorForm(_CadastroBase):
    is_staff = True

    codigo = forms.CharField(
        label='Código de acesso',
        help_text='Fornecido pela administração do sistema.',
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    def clean_codigo(self):
        esperado = settings.GESTOR_CODIGO_CONVITE
        if not esperado:
            raise forms.ValidationError('O cadastro de gestor está desativado no momento.')
        informado = self.cleaned_data['codigo']
        if not secrets.compare_digest(informado.encode(), esperado.encode()):
            raise forms.ValidationError('Código de acesso inválido.')
        return informado
