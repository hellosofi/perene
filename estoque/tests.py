"""Testes do app estoque.

Organização (pirâmide de testes):
  - Unidade: regras dos modelos e validação dos formulários.
  - Integração: views com banco de dados, filtros e isolamento entre mercados.
Os testes de sistema (Selenium) ficam em tests_selenium.py.
"""
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from perene.fabricas import (
    BaseTeste, criar_gestor, criar_funcionario, criar_lote, criar_mercado,
    criar_produto, dias_a_partir_de_hoje,
)

from .forms import LoteForm, ProdutoForm
from .models import Lote, Produto



# UNIDADE: modelos


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


class SituacaoLoteValoresLimiteTests(BaseTeste):
    """Testa as fronteiras das regras com a data congelada (mock de localdate).

    Sem o mock, o resultado dependeria do dia em que o teste roda
    (princípio R do FIRST: testes determinísticos).
    """
    HOJE = date(2026, 1, 15)

    def setUp(self):
        congelador = patch('estoque.models.timezone.localdate', return_value=self.HOJE)
        congelador.start()
        self.addCleanup(congelador.stop)
        self.produto = criar_produto(dias_alerta=7)

    def lote_com_validade(self, dias):
        return criar_lote(self.produto, validade=self.HOJE + timedelta(days=dias))

    def test_vence_hoje_fica_atencao_e_nao_critico(self):
        self.assertEqual(self.lote_com_validade(0).situacao, 'atencao')

    def test_venceu_ontem_fica_critico(self):
        self.assertEqual(self.lote_com_validade(-1).situacao, 'critico')

    def test_vence_exatamente_no_ultimo_dia_do_alerta_fica_atencao(self):
        self.assertEqual(self.lote_com_validade(7).situacao, 'atencao')

    def test_vence_um_dia_depois_do_alerta_fica_ok(self):
        self.assertEqual(self.lote_com_validade(8).situacao, 'ok')

    def test_lote_sem_validade_fica_ok(self):
        lote = criar_lote(self.produto, validade=None)
        self.assertEqual(lote.situacao, 'ok')

    def test_dias_de_alerta_personalizado_ainda_ok_fora_da_janela(self):
        self.produto.dias_alerta = 2
        self.assertEqual(self.lote_com_validade(3).situacao, 'ok')

    def test_dias_de_alerta_personalizado_atencao_dentro_da_janela(self):
        self.produto.dias_alerta = 2
        self.assertEqual(self.lote_com_validade(2).situacao, 'atencao')

    def test_estoque_igual_ao_minimo_fica_ok(self):
        self.produto.estoque_minimo = 10
        self.assertEqual(self.lote_com_validade(30).situacao, 'ok')

    def test_estoque_um_abaixo_do_minimo_fica_atencao(self):
        self.produto.estoque_minimo = 11
        self.assertEqual(self.lote_com_validade(30).situacao, 'atencao')

    def test_minimo_zero_nunca_gera_alerta(self):
        self.produto.estoque_minimo = 0
        self.assertEqual(self.lote_com_validade(30).situacao, 'ok')

    def test_avariado_prevalece_sobre_validade_distante(self):
        lote = criar_lote(self.produto, validade=self.HOJE + timedelta(days=90), avariado=True)
        self.assertEqual(lote.situacao, 'critico')

    def test_situacao_label_do_lote(self):
        self.assertEqual(self.lote_com_validade(-1).situacao_label, 'Crítico')


class ProdutoModelTests(BaseTeste):
    def setUp(self):
        self.produto = criar_produto(nome='Iogurte', codigo='789')

    def test_str_mostra_codigo_e_nome(self):
        self.assertEqual(str(self.produto), '[789] Iogurte')

    def test_quantidade_total_sem_lotes_e_zero(self):
        self.assertEqual(self.produto.quantidade_total, 0)

    def test_quantidade_total_soma_os_lotes(self):
        criar_lote(self.produto, quantidade=4)
        criar_lote(self.produto, quantidade=6)
        self.assertEqual(self.produto.quantidade_total, 10)

    def test_situacao_sem_lotes(self):
        self.assertEqual(self.produto.situacao, 'sem_lotes')

    def test_situacao_label_sem_lotes(self):
        self.assertEqual(self.produto.situacao_label, 'Sem lotes')

    def test_situacao_com_todos_os_lotes_ok(self):
        criar_lote(self.produto, validade=dias_a_partir_de_hoje(60))
        self.assertEqual(self.produto.situacao, 'ok')

    def test_situacao_pega_o_lote_mais_grave_atencao(self):
        criar_lote(self.produto, validade=dias_a_partir_de_hoje(60))
        criar_lote(self.produto, validade=dias_a_partir_de_hoje(2))
        self.assertEqual(self.produto.situacao, 'atencao')

    def test_situacao_pega_o_lote_mais_grave_critico(self):
        criar_lote(self.produto, validade=dias_a_partir_de_hoje(2))
        criar_lote(self.produto, validade=dias_a_partir_de_hoje(-3))
        self.assertEqual(self.produto.situacao, 'critico')

    # def test_status_label_conhecido(self):
    #     self.produto.status = 'low_stock'
    #     self.assertEqual(self.produto.status_label, 'Estoque baixo')

    # def test_status_label_desconhecido_devolve_o_proprio_valor(self):
    #     self.produto.status = 'inventado'
    #     self.assertEqual(self.produto.status_label, 'inventado')

    # def test_status_css_conhecido(self):
    #     self.produto.status = 'damaged'
    #     self.assertEqual(self.produto.status_css, 'etiqueta-danificado')

    # def test_status_css_desconhecido_fica_vazio(self):
    #     self.produto.status = 'inventado'
    #     self.assertEqual(self.produto.status_css, '')

    # def test_tudo_certo_nao_tem_ocorrencia(self):
    #     self.assertFalse(self.produto.tem_ocorrencia)

    # def test_outro_status_tem_ocorrencia(self):
    #     self.produto.status = 'surplus'
    #     self.assertTrue(self.produto.tem_ocorrencia)

    def test_valores_padrao_do_produto(self):
        self.assertEqual((self.produto.estoque_minimo, self.produto.dias_alerta), (0, 7))


class LoteModelTests(BaseTeste):
    def test_str_mostra_produto_quantidade_e_local(self):
        lote = criar_lote(criar_produto(nome='Arroz'), quantidade=5, local='Prateleira 3')
        self.assertEqual(str(lote), 'Arroz: 5 (Prateleira 3)')

    def test_apagar_produto_apaga_os_lotes(self):
        produto = criar_produto()
        criar_lote(produto)
        produto.delete()
        self.assertEqual(Lote.objects.count(), 0)


# ---------------------------------------------------------------------------
# UNIDADE: formulários
# ---------------------------------------------------------------------------

class ProdutoFormTests(TestCase):
    DADOS = {
        'nome': 'Iogurte', 'codigo': '123', 'categoria': 'Frios',
        'unidade': 'un.', 'estoque_minimo': 5, 'dias_alerta': 7, 'detalhe': '',
    }

    def test_dados_completos_sao_validos(self):
        self.assertTrue(ProdutoForm(self.DADOS).is_valid())

    def test_nome_e_obrigatorio(self):
        form = ProdutoForm({**self.DADOS, 'nome': ''})
        self.assertIn('nome', form.errors)

    def test_estoque_minimo_negativo_e_invalido(self):
        form = ProdutoForm({**self.DADOS, 'estoque_minimo': -1})
        self.assertIn('estoque_minimo', form.errors)

    def test_dias_alerta_negativo_e_invalido(self):
        form = ProdutoForm({**self.DADOS, 'dias_alerta': -3})
        self.assertIn('dias_alerta', form.errors)

    def test_estoque_minimo_com_texto_e_invalido(self):
        form = ProdutoForm({**self.DADOS, 'estoque_minimo': 'muito'})
        self.assertIn('estoque_minimo', form.errors)

    def test_codigo_e_categoria_sao_opcionais(self):
        form = ProdutoForm({**self.DADOS, 'codigo': '', 'categoria': ''})
        self.assertTrue(form.is_valid())

    def test_formulario_nao_expoe_o_campo_mercado(self):
        self.assertNotIn('mercado', ProdutoForm().fields)


class LoteFormTests(TestCase):
    DADOS = {'quantidade': 10, 'validade': '2030-01-31', 'local': 'Setor A', 'observacao': ''}

    def test_dados_completos_sao_validos(self):
        self.assertTrue(LoteForm(self.DADOS).is_valid())

    def test_quantidade_e_obrigatoria(self):
        form = LoteForm({**self.DADOS, 'quantidade': ''})
        self.assertIn('quantidade', form.errors)

    def test_quantidade_negativa_e_invalida(self):
        form = LoteForm({**self.DADOS, 'quantidade': -5})
        self.assertIn('quantidade', form.errors)

    def test_local_e_obrigatorio(self):
        form = LoteForm({**self.DADOS, 'local': ''})
        self.assertIn('local', form.errors)

    def test_validade_e_opcional(self):
        form = LoteForm({**self.DADOS, 'validade': ''})
        self.assertTrue(form.is_valid())

    def test_data_de_validade_invalida_e_recusada(self):
        form = LoteForm({**self.DADOS, 'validade': '31/02/2030'})
        self.assertIn('validade', form.errors)

    def test_avariado_comeca_desmarcado(self):
        form = LoteForm(self.DADOS)
        form.is_valid()
        self.assertFalse(form.cleaned_data['avariado'])

    def test_formulario_nao_expoe_o_produto(self):
        self.assertNotIn('produto', LoteForm().fields)


# ---------------------------------------------------------------------------
# INTEGRAÇÃO: views com banco de dados
# ---------------------------------------------------------------------------

class ListaProdutosViewTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.gestor = criar_gestor(self.mercado)
        self.client.force_login(self.gestor)
        self.url = reverse('lista_produtos')

    def test_pagina_abre_com_o_template_do_estoque(self):
        resposta = self.client.get(self.url)
        self.assertTemplateUsed(resposta, 'estoque/lista_produtos.html')

    def test_estoque_vazio_mostra_zeros(self):
        contexto = self.client.get(self.url).context
        self.assertEqual((contexto['total'], contexto['atencao'], contexto['pct_saudavel']), (0, 0, 0))

    def test_contadores_com_um_produto_saudavel_e_um_critico(self):
        saudavel = criar_produto(self.mercado, nome='Arroz')
        criar_lote(saudavel, validade=dias_a_partir_de_hoje(90))
        vencido = criar_produto(self.mercado, nome='Leite')
        criar_lote(vencido, validade=dias_a_partir_de_hoje(-2))
        contexto = self.client.get(self.url).context
        self.assertEqual((contexto['total'], contexto['atencao'], contexto['pct_saudavel']), (2, 1, 50.0))

    def test_lotes_sao_agrupados_por_situacao(self):
        produto = criar_produto(self.mercado)
        criar_lote(produto, validade=dias_a_partir_de_hoje(90))
        criar_lote(produto, validade=dias_a_partir_de_hoje(2))
        criar_lote(produto, validade=dias_a_partir_de_hoje(-1))
        grupos = self.client.get(self.url).context['grupos']
        self.assertEqual([len(g['items']) for g in grupos], [1, 1, 1])

    def test_lotes_ficam_ordenados_pela_validade_mais_proxima(self):
        produto = criar_produto(self.mercado)
        longe = criar_lote(produto, validade=dias_a_partir_de_hoje(90))
        perto = criar_lote(produto, validade=dias_a_partir_de_hoje(10))
        self.assertEqual(self.client.get(self.url).context['lotes'], [perto, longe])

    def test_busca_por_nome_filtra_os_lotes(self):
        leite = criar_produto(self.mercado, nome='Leite integral')
        arroz = criar_produto(self.mercado, nome='Arroz')
        lote_leite = criar_lote(leite)
        criar_lote(arroz)
        resposta = self.client.get(self.url, {'q': 'leite'})
        self.assertEqual(resposta.context['lotes'], [lote_leite])

    def test_busca_por_local_filtra_os_lotes(self):
        produto = criar_produto(self.mercado)
        na_camara = criar_lote(produto, local='Câmara fria')
        criar_lote(produto, local='Balcão')
        resposta = self.client.get(self.url, {'q': 'câmara'})
        self.assertEqual(resposta.context['lotes'], [na_camara])

    def test_filtro_por_categoria(self):
        frios = criar_produto(self.mercado, nome='Queijo', categoria='Frios')
        secos = criar_produto(self.mercado, nome='Feijão', categoria='Secos')
        lote_frios = criar_lote(frios)
        criar_lote(secos)
        resposta = self.client.get(self.url, {'categoria': 'Frios'})
        self.assertEqual(resposta.context['lotes'], [lote_frios])

    def test_filtro_por_situacao_critico(self):
        produto = criar_produto(self.mercado)
        criar_lote(produto, validade=dias_a_partir_de_hoje(90))
        vencido = criar_lote(produto, validade=dias_a_partir_de_hoje(-5))
        resposta = self.client.get(self.url, {'status': 'critico'})
        self.assertEqual(resposta.context['lotes'], [vencido])

    def test_filtro_por_produto(self):
        a = criar_produto(self.mercado, nome='A')
        b = criar_produto(self.mercado, nome='B')
        lote_a = criar_lote(a)
        criar_lote(b)
        resposta = self.client.get(self.url, {'produto': a.pk})
        self.assertEqual(resposta.context['lotes'], [lote_a])

    def test_filtro_de_produto_nao_numerico_e_ignorado(self):
        produto = criar_produto(self.mercado)
        lote = criar_lote(produto)
        resposta = self.client.get(self.url, {'produto': 'abc'})
        self.assertEqual(resposta.context['lotes'], [lote])

    def test_categorias_sem_repeticao_e_sem_vazias(self):
        criar_produto(self.mercado, nome='A', categoria='Frios')
        criar_produto(self.mercado, nome='B', categoria='Frios')
        criar_produto(self.mercado, nome='C', categoria='')
        resposta = self.client.get(self.url)
        self.assertEqual(list(resposta.context['categorias']), ['Frios'])

    def test_visao_padrao_e_quadro(self):
        self.assertEqual(self.client.get(self.url).context['visao'], 'quadro')

    def test_visao_lista_e_respeitada(self):
        self.assertEqual(self.client.get(self.url, {'visao': 'lista'}).context['visao'], 'lista')


class IsolamentoEntreMercadosTests(BaseTeste):
    """Um mercado nunca pode ver nem mexer nos dados de outro."""

    def setUp(self):
        self.meu_mercado = criar_mercado('Meu mercado')
        self.outro_mercado = criar_mercado('Outro mercado')
        self.gestor = criar_gestor(self.meu_mercado)
        self.client.force_login(self.gestor)
        self.produto_alheio = criar_produto(self.outro_mercado, nome='Produto alheio')
        self.lote_alheio = criar_lote(self.produto_alheio)

    def test_lista_nao_mostra_lotes_de_outro_mercado(self):
        resposta = self.client.get(reverse('lista_produtos'))
        self.assertEqual(resposta.context['lotes'], [])

    def test_contadores_nao_contam_produtos_de_outro_mercado(self):
        resposta = self.client.get(reverse('lista_produtos'))
        self.assertEqual(resposta.context['total'], 0)

    def test_nao_deixa_filtrar_pelo_id_de_produto_de_outro_mercado(self):
        resposta = self.client.get(reverse('lista_produtos'), {'produto': self.produto_alheio.pk})
        self.assertIsNone(resposta.context['produto_selecionado'])

    def test_registrar_lote_em_produto_de_outro_mercado_da_404_no_get(self):
        resposta = self.client.get(reverse('adicionar_lote', args=[self.produto_alheio.pk]))
        self.assertEqual(resposta.status_code, 404)

    def test_registrar_lote_em_produto_de_outro_mercado_da_404_no_post(self):
        dados = {'quantidade': 5, 'local': 'Setor A'}
        resposta = self.client.post(reverse('adicionar_lote', args=[self.produto_alheio.pk]), dados)
        self.assertEqual(resposta.status_code, 404)

    def test_post_recusado_nao_cria_lote_no_produto_alheio(self):
        dados = {'quantidade': 5, 'local': 'Setor A'}
        self.client.post(reverse('adicionar_lote', args=[self.produto_alheio.pk]), dados)
        self.assertEqual(self.produto_alheio.lotes.count(), 1)


class AdicionarProdutoViewTests(BaseTeste):
    DADOS = {
        'nome': 'Iogurte natural', 'codigo': '7891', 'categoria': 'Frios',
        'unidade': 'un.', 'estoque_minimo': 5, 'dias_alerta': 7, 'detalhe': '',
    }

    def setUp(self):
        self.mercado = criar_mercado()
        self.client.force_login(criar_gestor(self.mercado))
        self.url = reverse('adicionar_produto')

    def test_get_abre_a_lista_com_o_modal_aberto(self):
        resposta = self.client.get(self.url)
        self.assertTrue(resposta.context['mostrar_modal'])

    def test_post_valido_redireciona_para_o_estoque(self):
        resposta = self.client.post(self.url, self.DADOS)
        self.assertRedirects(resposta, reverse('lista_produtos'))

    def test_post_valido_cria_o_produto(self):
        self.client.post(self.url, self.DADOS)
        self.assertTrue(Produto.objects.filter(nome='Iogurte natural').exists())

    def test_produto_criado_pertence_ao_mercado_do_usuario(self):
        self.client.post(self.url, self.DADOS)
        self.assertEqual(Produto.objects.get(nome='Iogurte natural').mercado, self.mercado)

    def test_mercado_enviado_no_post_e_ignorado(self):
        invasor = criar_mercado('Mercado invasor')
        self.client.post(self.url, {**self.DADOS, 'mercado': invasor.pk})
        self.assertEqual(Produto.objects.get(nome='Iogurte natural').mercado, self.mercado)

    def test_post_sem_nome_nao_cria_produto(self):
        self.client.post(self.url, {**self.DADOS, 'nome': ''})
        self.assertEqual(Produto.objects.count(), 0)

    def test_post_sem_nome_reabre_o_modal_com_o_erro(self):
        resposta = self.client.post(self.url, {**self.DADOS, 'nome': ''})
        self.assertIn('nome', resposta.context['form_produto'].errors)

    def test_post_invalido_responde_200_e_nao_redireciona(self):
        resposta = self.client.post(self.url, {**self.DADOS, 'estoque_minimo': -1})
        self.assertEqual(resposta.status_code, 200)


class AdicionarLoteViewTests(BaseTeste):
    DADOS = {'quantidade': 12, 'validade': '2030-05-20', 'local': 'Câmara fria', 'observacao': ''}

    def setUp(self):
        self.mercado = criar_mercado()
        self.client.force_login(criar_funcionario(self.mercado))
        self.produto = criar_produto(self.mercado, nome='Queijo')
        self.url = reverse('adicionar_lote', args=[self.produto.pk])

    def test_get_mostra_o_formulario_do_produto(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context['produto'], self.produto)

    def test_get_usa_o_template_de_registro_de_lote(self):
        self.assertTemplateUsed(self.client.get(self.url), 'estoque/adicionar_lote.html')

    def test_post_valido_redireciona_para_o_estoque(self):
        self.assertRedirects(self.client.post(self.url, self.DADOS), reverse('lista_produtos'))

    def test_post_valido_cria_o_lote_no_produto(self):
        self.client.post(self.url, self.DADOS)
        self.assertEqual(self.produto.lotes.get().local, 'Câmara fria')

    def test_funcionario_tambem_pode_registrar_lote(self):
        self.client.post(self.url, self.DADOS)
        self.assertEqual(self.produto.quantidade_total, 12)

    def test_post_com_quantidade_negativa_nao_cria_lote(self):
        self.client.post(self.url, {**self.DADOS, 'quantidade': -1})
        self.assertEqual(Lote.objects.count(), 0)

    def test_post_sem_local_mostra_o_erro_no_formulario(self):
        resposta = self.client.post(self.url, {**self.DADOS, 'local': ''})
        self.assertIn('local', resposta.context['form'].errors)

    def test_produto_inexistente_da_404(self):
        resposta = self.client.get(reverse('adicionar_lote', args=[99999]))
        self.assertEqual(resposta.status_code, 404)

    def test_produto_enviado_no_post_e_ignorado(self):
        outro = criar_produto(self.mercado, nome='Outro')
        self.client.post(self.url, {**self.DADOS, 'produto': outro.pk})
        self.assertEqual(outro.lotes.count(), 0)
