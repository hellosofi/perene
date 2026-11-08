"""Testes do app funcionarios (tela de equipe, só para gestores).

  - Unidade: modelos Funcionario e Tarefa.
  - Integração: a view equipe, com banco de dados e permissões.
Os testes de sistema (Selenium) ficam em tests_selenium.py.
"""
from datetime import time

from django.urls import reverse

from perene.fabricas import (
    BaseTeste, criar_funcionario, criar_gestor, criar_membro, criar_mercado, criar_tarefa,
)

from .models import Funcionario, Tarefa



# UNIDADE: modelos


class FuncionarioModelTests(BaseTeste):
    def test_str_e_o_nome(self):
        self.assertEqual(str(criar_membro(None, nome='Ana Souza')), 'Ana Souza')

    def test_apagar_o_mercado_apaga_a_equipe(self):
        mercado = criar_mercado()
        criar_membro(mercado)
        mercado.delete()
        self.assertEqual(Funcionario.objects.count(), 0)


class TarefaModelTests(BaseTeste):
    def test_str_e_o_titulo(self):
        self.assertEqual(str(criar_tarefa(None, titulo='Limpar balcão')), 'Limpar balcão')

    def test_tarefa_comeca_nao_concluida(self):
        self.assertFalse(criar_tarefa(None).concluida)

    def test_tarefa_pode_ficar_sem_responsavel(self):
        self.assertIsNone(criar_tarefa(None).responsavel)

    def test_apagar_o_responsavel_mantem_a_tarefa_sem_dono(self):
        membro = criar_membro(None)
        tarefa = criar_tarefa(None, responsavel=membro)
        membro.delete()
        tarefa.refresh_from_db()
        self.assertIsNone(tarefa.responsavel)

    def test_horario_e_opcional(self):
        self.assertIsNone(criar_tarefa(None).horario)

    def test_tarefa_guarda_o_horario(self):
        tarefa = criar_tarefa(None, horario=time(14, 30))
        tarefa.refresh_from_db()
        self.assertEqual(tarefa.horario, time(14, 30))

    def test_funcionario_enxerga_suas_tarefas_pelo_related_name(self):
        membro = criar_membro(None)
        tarefa = criar_tarefa(None, responsavel=membro)
        self.assertEqual(list(membro.tarefas.all()), [tarefa])


# ---------------------------------------------------------------------------
# INTEGRAÇÃO: view equipe
# ---------------------------------------------------------------------------

class EquipeViewTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.client.force_login(criar_gestor(self.mercado))
        self.url = reverse('funcionarios')

    def test_pagina_abre_com_o_template_da_equipe(self):
        self.assertTemplateUsed(self.client.get(self.url), 'funcionarios/equipe.html')

    def test_equipe_vazia_mostra_zeros(self):
        contexto = self.client.get(self.url).context
        self.assertEqual(
            (contexto['total_funcionarios'], contexto['total_tarefas'], contexto['pct_conclusao']),
            (0, 0, 0),
        )

    def test_conta_os_funcionarios_do_mercado(self):
        criar_membro(self.mercado, nome='Ana')
        criar_membro(self.mercado, nome='Bia')
        self.assertEqual(self.client.get(self.url).context['total_funcionarios'], 2)

    def test_porcentagem_de_conclusao_com_uma_de_quatro(self):
        criar_tarefa(self.mercado, concluida=True)
        criar_tarefa(self.mercado)
        criar_tarefa(self.mercado)
        criar_tarefa(self.mercado)
        self.assertEqual(self.client.get(self.url).context['pct_conclusao'], 25)

    def test_porcentagem_de_conclusao_arredonda(self):
        criar_tarefa(self.mercado, concluida=True)
        criar_tarefa(self.mercado)
        criar_tarefa(self.mercado)
        self.assertEqual(self.client.get(self.url).context['pct_conclusao'], 33)

    def test_todas_concluidas_da_cem_por_cento(self):
        criar_tarefa(self.mercado, concluida=True)
        criar_tarefa(self.mercado, concluida=True)
        self.assertEqual(self.client.get(self.url).context['pct_conclusao'], 100)

    def test_conta_tarefas_concluidas_e_totais(self):
        criar_tarefa(self.mercado, concluida=True)
        criar_tarefa(self.mercado)
        contexto = self.client.get(self.url).context
        self.assertEqual((contexto['tarefas_concluidas'], contexto['total_tarefas']), (1, 2))

    def test_cada_funcionario_traz_o_total_de_tarefas_e_as_concluidas(self):
        ana = criar_membro(self.mercado, nome='Ana')
        criar_tarefa(self.mercado, responsavel=ana, concluida=True)
        criar_tarefa(self.mercado, responsavel=ana)
        da_ana = self.client.get(self.url).context['funcionarios'].get(pk=ana.pk)
        self.assertEqual((da_ana.total_tarefas, da_ana.tarefas_concluidas), (2, 1))

    def test_pagina_mostra_o_nome_do_funcionario(self):
        criar_membro(self.mercado, nome='Ana Souza')
        self.assertContains(self.client.get(self.url), 'Ana Souza')

    def test_pagina_mostra_o_titulo_da_tarefa(self):
        criar_tarefa(self.mercado, titulo='Conferir validade dos frios')
        self.assertContains(self.client.get(self.url), 'Conferir validade dos frios')

    def test_pagina_mostra_o_codigo_de_convite_do_mercado(self):
        self.assertContains(self.client.get(self.url), self.mercado.codigo_convite)

    def test_nao_mostra_equipe_de_outro_mercado(self):
        criar_membro(criar_mercado('Outro'), nome='Intrusa')
        self.assertNotContains(self.client.get(self.url), 'Intrusa')

    def test_nao_conta_tarefas_de_outro_mercado(self):
        criar_tarefa(criar_mercado('Outro'))
        self.assertEqual(self.client.get(self.url).context['total_tarefas'], 0)

    def test_nao_mostra_o_codigo_de_convite_de_outro_mercado(self):
        outro = criar_mercado('Outro')
        self.assertNotContains(self.client.get(self.url), outro.codigo_convite)


class EquipePermissaoTests(BaseTeste):
    def test_funcionario_comum_e_barrado(self):
        self.client.force_login(criar_funcionario(criar_mercado()))
        self.assertRedirects(self.client.get(reverse('funcionarios')), reverse('lista_produtos'))

    def test_visitante_e_mandado_para_a_pagina_inicial(self):
        resposta = self.client.get(reverse('funcionarios'))
        self.assertRedirects(
            resposta, f"{reverse('index')}?next={reverse('funcionarios')}",
            fetch_redirect_response=False,
        )
