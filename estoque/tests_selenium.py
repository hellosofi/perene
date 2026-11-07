from django.test import override_settings
from django.utils import timezone
from os import link

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

import time

from estoque.models import Produto 

class BaseTestCase(StaticLiveServerTestCase):
    """
    Classe-base que inicializa e encerra o Chrome em modo headless
    (sem interface gráfica) antes e depois de cada teste.

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
        # opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,800")

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=opts)

        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    # -------------------------------------------------------------------------
    # Inserção dos métodos aqui
    # ---------------------------------------------