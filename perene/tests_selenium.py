"""Testes de sistema (ponta a ponta) do acesso ao Perene: cadastro, login e saída.

Simulam uma pessoa usando o navegador de verdade (Chrome, via Selenium).
São poucos de propósito: são lentos e mais frágeis que os testes de unidade
e de integração (veja a pirâmide de testes).

Como rodar só estes:   python manage.py test perene.tests_selenium
Como pular estes:      python manage.py test --exclude-tag=selenium
"""
from django.test import override_settings, tag

from perene.fabricas import criar_funcionario, criar_gestor, criar_mercado
from perene.models import Mercado
from perene.selenium_base import BaseTestCase

CODIGO_GESTOR = 'codigo-selenium'
FORMULARIO = 'form.auth-formulario__conteudo'


@tag('selenium')
@override_settings(GESTOR_CODIGO_CONVITE=CODIGO_GESTOR)
class FluxoDeAcessoSeleniumTests(BaseTestCase):

    def test_gestor_cria_conta_e_chega_ao_estoque(self):
        self.abrir('cadastro_gestor')
        self.preencher('id_nome', 'Carlos Lima')
        self.preencher('id_email', 'carlos@mercado.com')
        self.preencher('id_senha', 'Senha-Forte-123')
        self.preencher('id_confirmar_senha', 'Senha-Forte-123')
        self.preencher('id_codigo', CODIGO_GESTOR)
        self.preencher('id_nome_mercado', 'Mercado Sol')
        self.preencher('id_cidade_mercado', 'Olinda')
        self.enviar(FORMULARIO)
        self.esperar_url('/estoque/')
        self.assertEqual(self.texto_de('.titulo-pagina h1'), 'Inventário')

    def test_funcionario_cria_conta_com_o_codigo_do_mercado(self):
        mercado = criar_mercado('Mercado Lua')
        self.abrir('cadastro_funcionario')
        self.preencher('id_nome', 'Maria Souza')
        self.preencher('id_email', 'maria@mercado.com')
        self.preencher('id_senha', 'Senha-Forte-123')
        self.preencher('id_confirmar_senha', 'Senha-Forte-123')
        self.preencher('id_codigo_mercado', mercado.codigo_convite)
        self.enviar(FORMULARIO)
        self.esperar_url('/estoque/')
        self.assertEqual(self.texto_de('.perfil-loja span'), 'Funcionário')

    def test_codigo_de_gestor_errado_mostra_erro_e_nao_cria_mercado(self):
        self.abrir('cadastro_gestor')
        self.preencher('id_nome', 'Carlos Lima')
        self.preencher('id_email', 'carlos@mercado.com')
        self.preencher('id_senha', 'Senha-Forte-123')
        self.preencher('id_confirmar_senha', 'Senha-Forte-123')
        self.preencher('id_codigo', 'codigo-errado')
        self.preencher('id_nome_mercado', 'Mercado Sol')
        self.enviar(FORMULARIO)
        self.assertEqual(self.texto_de('.campo__erro'), 'Código de acesso inválido.')
        self.assertEqual(Mercado.objects.count(), 0)

    def test_login_com_senha_errada_mostra_a_mensagem_de_erro(self):
        criar_funcionario(criar_mercado(), email='func@mercado.com')
        self.abrir('login_funcionario')
        self.preencher('id_email', 'func@mercado.com')
        self.preencher('id_senha', 'senha-errada')
        self.enviar(FORMULARIO)
        self.assertEqual(self.texto_de('.aviso--erro'), 'E-mail ou senha incorretos.')

    def test_visitante_que_abre_o_estoque_volta_para_a_pagina_inicial(self):
        self.abrir('lista_produtos')
        self.esperar_url('/perene/')
        self.assertFalse(self.existe('.barra-lateral'))

    def test_gestor_entra_e_sai_da_conta(self):
        criar_gestor(criar_mercado(), email='chefe@mercado.com')
        self.entrar_como_gestor('chefe@mercado.com')
        self.clicar("form[action$='/perene/sair/'] button")
        self.esperar_url('/perene/')
        self.abrir('lista_produtos')
        self.esperar_url('next=')
