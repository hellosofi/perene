"""Base compartilhada dos testes de sistema (Selenium).

Mantém o BaseTestCase do modelo da disciplina e acrescenta métodos de apoio
(abrir páginas, preencher campos, entrar pela tela de login). Os arquivos
tests_selenium.py de cada app herdam desta classe.

Para rodar sem abrir a janela do Chrome:  SELENIUM_HEADLESS=1
Para ver o navegador mais devagar:         SELENIUM_PAUSA=1   (segundos entre os passos)
"""
import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from perene.fabricas import HASH_RAPIDO, SENHA

PAUSA = float(os.environ.get('SELENIUM_PAUSA', '0'))


@override_settings(PASSWORD_HASHERS=HASH_RAPIDO)
class BaseTestCase(StaticLiveServerTestCase):
    """
    Classe-base que inicializa e encerra o Chrome antes e depois de cada
    classe de testes.
    StaticLiveServerTestCase sobe um servidor HTTP temporário em uma
    porta aleatória na própria máquina que está rodando os testes, usando
    um banco de dados de teste isolado, e disponibiliza self.live_server_url
    para que o Selenium possa acessá-lo.
    live_server_url aponta sempre para localhost. Ex: http://127.0.0.1:54321
    Esse servidor existe apenas durante a execução dos testes e é destruído
    logo depois.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        if os.environ.get('SELENIUM_HEADLESS'):
            opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--window-size=1280,800')
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=opts)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # cada teste começa sem sessão aberta no navegador
        self.driver.delete_all_cookies()

    # Métodos de apoio
   

    def pausa(self):
        """Espera um pouco entre os passos (só se SELENIUM_PAUSA estiver definida)."""
        time.sleep(PAUSA)

    def abrir(self, nome_da_rota, *args):
        self.pausa()
        self.driver.get(self.live_server_url + reverse(nome_da_rota, args=args))

    def preencher(self, id_do_campo, valor):
        campo = self.wait.until(EC.visibility_of_element_located((By.ID, id_do_campo)))
        self.pausa()
        campo.clear()
        campo.send_keys(valor)

    def clicar(self, seletor_css):
        self.pausa()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_css))).click()

    def enviar(self, seletor_do_formulario):
        self.clicar(f"{seletor_do_formulario} button[type='submit']")

    def esperar_url(self, trecho):
        self.wait.until(EC.url_contains(trecho))

    def texto_de(self, seletor_css):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, seletor_css))).text

    def existe(self, seletor_css):
        return len(self.driver.find_elements(By.CSS_SELECTOR, seletor_css)) > 0

    def entrar_como_gestor(self, email):
        self.abrir('login_gestor')
        self.preencher('id_usuario', email)
        self.preencher('id_senha', SENHA)
        self.enviar('form.auth-formulario__conteudo')
        self.esperar_url('/estoque/')

    def entrar_como_funcionario(self, email):
        self.abrir('login_funcionario')
        self.preencher('id_email', email)
        self.preencher('id_senha', SENHA)
        self.enviar('form.auth-formulario__conteudo')
        self.esperar_url('/estoque/')