"""Funções auxiliares para montar dados de teste (fixtures).

O nome não começa com "test" de propósito, para o Django não tratar este
arquivo como módulo de testes.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from estoque.models import Lote, Produto
from funcionarios.models import Funcionario, Tarefa
from perene.models import Mercado, Perfil

User = get_user_model()

SENHA = 'Senha-Forte-123'

# O hash de senha padrão do Django é lento de propósito. Nos testes usamos um
# hash simples para a suíte continuar rápida (princípio F do FIRST).
HASH_RAPIDO = ['django.contrib.auth.hashers.MD5PasswordHasher']


@override_settings(PASSWORD_HASHERS=HASH_RAPIDO)
class BaseTeste(TestCase):
    """TestCase com hash de senha rápido. Os testes do projeto herdam dela."""


def criar_mercado(nome='Mercado Central', cidade='Recife'):
    return Mercado.objects.create(nome=nome, cidade=cidade)


def criar_usuario(email, papel, mercado, nome='Pessoa', senha=SENHA):
    """Cria o usuário e o perfil. Gestor é is_staff, como no cadastro real."""
    usuario = User.objects.create_user(
        username=email, email=email, password=senha,
        first_name=nome, is_staff=(papel == 'gestor'),
    )
    Perfil.objects.create(usuario=usuario, mercado=mercado, papel=papel)
    return usuario


def criar_gestor(mercado, email='gestor@mercado.com', nome='Gestora'):
    return criar_usuario(email, 'gestor', mercado, nome)


def criar_funcionario(mercado, email='func@mercado.com', nome='Funcionário'):
    return criar_usuario(email, 'funcionario', mercado, nome)


def criar_produto(mercado=None, nome='Leite', **campos):
    return Produto.objects.create(mercado=mercado, nome=nome, **campos)


def criar_lote(produto, **campos):
    dados = {'quantidade': 10, 'local': 'Setor A'}
    dados.update(campos)
    return Lote.objects.create(produto=produto, **dados)


def dias_a_partir_de_hoje(dias):
    return timezone.localdate() + timedelta(days=dias)


def criar_membro(mercado, nome='Ana Souza', iniciais='AS', cargo='Repositora', status='No turno'):
    return Funcionario.objects.create(
        mercado=mercado, nome=nome, iniciais=iniciais, cargo=cargo, status=status,
    )


def criar_tarefa(mercado, titulo='Repor iogurtes', responsavel=None, concluida=False, **campos):
    return Tarefa.objects.create(
        mercado=mercado, titulo=titulo, responsavel=responsavel,
        concluida=concluida, **campos,
    )
