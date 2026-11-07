from django.test import TestCase

# Create your tests here.
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Lote, Produto


class SituacaoLoteTests(TestCase):

    def setUp(self):
        self.produto = Produto.objects.create(nome='Leite')
        self.hoje = timezone.localdate()

    def criar_lote(self, **campos):
        dados = {'produto': self.produto, 'quantidade': 10, 'local': 'Setor A'}
        dados.update(campos)
        return Lote.objects.create(**dados)

    def test_validade_distante_fica_ok(self):
        lote = self.criar_lote(validade=self.hoje + timedelta(days=30))
        self.assertEqual(lote.situacao, 'ok')

    def test_vence_em_3_dias_fica_atencao(self):
        lote = self.criar_lote(validade=self.hoje + timedelta(days=3))
        self.assertEqual(lote.situacao, 'atencao')

    def test_vencido_fica_critico(self):
        lote = self.criar_lote(validade=self.hoje - timedelta(days=1))
        self.assertEqual(lote.situacao, 'critico')

    def test_avariado_fica_critico(self):
        lote = self.criar_lote(validade=self.hoje + timedelta(days=30), avariado=True)
        self.assertEqual(lote.situacao, 'critico')

    def test_abaixo_do_minimo_fica_atencao(self):
        self.produto.estoque_minimo = 20
        self.produto.save()
        lote = self.criar_lote(validade=self.hoje + timedelta(days=30))
        self.assertEqual(lote.situacao, 'atencao')