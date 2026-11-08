"""Testes de sistema (ponta a ponta) do estoque.

Como rodar só estes:   python manage.py test estoque.tests_selenium
Como pular estes:      python manage.py test --exclude-tag=selenium
"""
from django.test import tag
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from perene.fabricas import (
    criar_funcionario, criar_gestor, criar_lote, criar_mercado,
    criar_produto, dias_a_partir_de_hoje,
)
from perene.selenium_base import BaseTestCase

CARDS = '.card-produto'


@tag('selenium')
class FluxoDeEstoqueSeleniumTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.mercado = criar_mercado()
        criar_gestor(self.mercado, email='chefe@mercado.com')

    def test_gestor_cadastra_um_produto_pelo_modal(self):
        self.entrar_como_gestor('chefe@mercado.com')
        self.clicar("section.titulo-pagina a[href$='/estoque/adicionar/']")
        self.preencher('id_nome', 'Iogurte natural')
        self.preencher('id_codigo', '7891000')
        self.preencher('id_categoria', 'Frios')
        self.preencher('id_unidade', 'un.')
        self.preencher('id_estoque_minimo', '5')
        self.preencher('id_dias_alerta', '7')
        self.enviar('form.modal')
        self.wait.until(lambda d: not self.existe('form.modal'))
        opcoes = Select(self.driver.find_element(By.NAME, 'produto')).options
        self.assertIn('Iogurte natural', [o.text.strip() for o in opcoes])

    def test_gestor_registra_um_lote_e_ve_o_card_no_estoque(self):
        criar_produto(self.mercado, nome='Queijo minas', categoria='Frios')
        self.entrar_como_gestor('chefe@mercado.com')
        Select(self.driver.find_element(By.NAME, 'produto')).select_by_visible_text('Queijo minas')
        self.clicar("a.botao-primario[href*='/lotes/adicionar/']")
        self.preencher('id_quantidade', '12')
        self.preencher('id_local', 'Câmara fria')
        self.enviar('form.registrar-lote')
        self.esperar_url('/estoque/')
        self.assertEqual(self.texto_de(f'{CARDS} h4'), 'Queijo minas')

    def test_lote_vencido_aparece_na_coluna_critico(self):
        produto = criar_produto(self.mercado, nome='Leite integral')
        criar_lote(produto, validade=dias_a_partir_de_hoje(-3))
        self.entrar_como_gestor('chefe@mercado.com')
        coluna_critico = "//section[contains(@class,'coluna')][.//h3[normalize-space()='Crítico']]"
        cards = self.driver.find_elements(By.XPATH, f"{coluna_critico}//article[contains(@class,'card-produto')]")
        self.assertEqual(len(cards), 1)

    def test_busca_mostra_so_o_produto_procurado(self):
        criar_lote(criar_produto(self.mercado, nome='Leite integral'))
        criar_lote(criar_produto(self.mercado, nome='Arroz branco'))
        self.entrar_como_gestor('chefe@mercado.com')
        campo = self.driver.find_element(By.NAME, 'q')
        campo.send_keys('arroz\n')
        self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, CARDS)) == 1)
        self.assertEqual(self.texto_de(f'{CARDS} h4'), 'Arroz branco')

    def test_filtro_de_ocorrencia_critico_esconde_os_lotes_saudaveis(self):
        produto = criar_produto(self.mercado, nome='Presunto')
        criar_lote(produto, validade=dias_a_partir_de_hoje(90), local='Balcão')
        criar_lote(produto, validade=dias_a_partir_de_hoje(-1), local='Câmara')
        self.entrar_como_gestor('chefe@mercado.com')
        self.driver.find_element(By.XPATH, "//div[@class='filtros']//button[normalize-space()='Crítico']").click()
        self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, CARDS)) == 1)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, CARDS)), 1)

    def test_funcionario_de_outro_mercado_nao_ve_os_produtos(self):
        criar_lote(criar_produto(self.mercado, nome='Produto do mercado A'))
        criar_funcionario(criar_mercado('Mercado B'), email='func@b.com')
        self.entrar_como_funcionario('func@b.com')
        self.assertFalse(self.existe(CARDS))
