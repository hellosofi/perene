"""Testes de sistema (ponta a ponta) da tela de equipe.

Como rodar só estes:   python manage.py test funcionarios.tests_selenium
Como pular estes:      python manage.py test --exclude-tag=selenium
"""
from django.test import tag

from perene.fabricas import criar_funcionario, criar_gestor, criar_membro, criar_mercado, criar_tarefa
from perene.selenium_base import BaseTestCase

LINK_EQUIPE = "a[href$='/funcionarios/funcionarios/']"


@tag('selenium')
class EquipeSeleniumTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.mercado = criar_mercado('Mercado Sol')

    def test_gestor_abre_a_equipe_pelo_menu_e_ve_o_codigo_do_mercado(self):
        criar_gestor(self.mercado, email='chefe@mercado.com')
        self.entrar_como_gestor('chefe@mercado.com')
        self.clicar(LINK_EQUIPE)
        self.assertEqual(self.texto_de('.titulo-pagina h1'), 'Minha equipe')
        self.assertIn(self.mercado.codigo_convite, self.texto_de('.codigo-mercado'))

    def test_equipe_mostra_a_pessoa_e_a_tarefa_cadastradas(self):
        ana = criar_membro(self.mercado, nome='Ana Souza')
        criar_tarefa(self.mercado, titulo='Repor iogurtes', responsavel=ana)
        criar_gestor(self.mercado, email='chefe@mercado.com')
        self.entrar_como_gestor('chefe@mercado.com')
        self.abrir('funcionarios')
        self.assertIn('Ana Souza', self.texto_de('.lista-equipe'))
        self.assertIn('Repor iogurtes', self.texto_de('.lista-tarefas'))

    def test_funcionario_nao_ve_o_link_da_equipe_no_menu(self):
        criar_funcionario(self.mercado, email='func@mercado.com')
        self.entrar_como_funcionario('func@mercado.com')
        self.assertFalse(self.existe(LINK_EQUIPE))

    def test_funcionario_que_digita_o_endereco_da_equipe_volta_ao_estoque_com_aviso(self):
        criar_funcionario(self.mercado, email='func@mercado.com')
        self.entrar_como_funcionario('func@mercado.com')
        self.abrir('funcionarios')
        self.esperar_url('/estoque/')
        self.assertIn('Acesso restrito', self.texto_de('.mensagens'))
