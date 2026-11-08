from django.urls import reverse
from selenium.webdriver.common.by import By
from perene.tests_selenium import BaseTestCase


class Olho(BaseTestCase):
    def test_olho(self):
        d = self.driver
        d.set_window_size(1440, 1000)
        d.get(self.live_server_url + reverse('login_funcionario'))
        d.find_element(By.NAME, 'senha').send_keys('segredo')
        caixa = d.find_element(By.CSS_SELECTOR, '.campo--senha')
        caixa.screenshot('C:/Users/infra/AppData/Local/Temp/claude/162fdbfb80279318/ea3ba3da-25c6-4168-8ced-460d3533ef8d/scratchpad/olho-1.png')
        d.find_element(By.CSS_SELECTOR, '[data-mostrar-senha]').click()
        caixa.screenshot('C:/Users/infra/AppData/Local/Temp/claude/162fdbfb80279318/ea3ba3da-25c6-4168-8ced-460d3533ef8d/scratchpad/olho-2.png')
