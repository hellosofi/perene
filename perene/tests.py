"""Testes do app perene (mercado, perfis, login, cadastro e notificações).

Organização (pirâmide de testes):
  - Unidade: modelos, utilitários, permissões e formulários.
  - Integração: telas de login/cadastro, logout e proteção de acesso.
Os testes de sistema (Selenium) ficam em tests_selenium.py.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, override_settings
from django.urls import reverse

from estoque.models import Produto

from .context_processors import notificacoes
from .decorators import eh_gestor
from .fabricas import (
    SENHA, BaseTeste, criar_funcionario, criar_gestor,
    criar_mercado, criar_produto,
)
from .forms import (
    CadastroFuncionarioForm, CadastroGestorForm,
    LoginFuncionarioForm, LoginGestorForm,
)
from .models import Mercado, Notificacao, Perfil, gerar_codigo_convite
from .utils import mercado_do_usuario

User = get_user_model()

CODIGO_GESTOR = 'codigo-de-teste'



# UNIDADE: modelos e utilitários


class CodigoConviteTests(BaseTeste):
    def test_codigo_tem_8_caracteres_hexadecimais_maiusculos(self):
        self.assertRegex(gerar_codigo_convite(), r'^[0-9A-F]{8}$')

    def test_dois_codigos_gerados_sao_diferentes(self):
        self.assertNotEqual(gerar_codigo_convite(), gerar_codigo_convite())


class MercadoModelTests(BaseTeste):
    def test_mercado_recebe_codigo_de_convite_automaticamente(self):
        self.assertRegex(criar_mercado().codigo_convite, r'^[0-9A-F]{8}$')

    def test_mercados_diferentes_tem_codigos_diferentes(self):
        a, b = criar_mercado('A'), criar_mercado('B')
        self.assertNotEqual(a.codigo_convite, b.codigo_convite)

    def test_codigo_de_convite_nao_e_editavel(self):
        self.assertFalse(Mercado._meta.get_field('codigo_convite').editable)

    def test_str_e_o_nome(self):
        self.assertEqual(str(criar_mercado('Mercado Sol')), 'Mercado Sol')

    def test_cidade_e_opcional(self):
        self.assertEqual(Mercado.objects.create(nome='Sem cidade').cidade, '')


class PerfilModelTests(BaseTeste):
    def test_str_mostra_usuario_papel_e_mercado(self):
        usuario = criar_gestor(criar_mercado('Mercado Sol'), email='ana@x.com')
        self.assertEqual(str(usuario.perfil), 'ana@x.com (Gestor) - Mercado Sol')

    def test_apagar_o_usuario_apaga_o_perfil(self):
        usuario = criar_funcionario(criar_mercado())
        usuario.delete()
        self.assertEqual(Perfil.objects.count(), 0)

    def test_apagar_o_mercado_apaga_os_perfis(self):
        mercado = criar_mercado()
        criar_funcionario(mercado)
        mercado.delete()
        self.assertEqual(Perfil.objects.count(), 0)


class NotificacaoModelTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()

    def nova(self, **campos):
        dados = {'tipo': 'comunicado', 'titulo': 'Aviso', 'mensagem': 'Texto', 'mercado': self.mercado}
        dados.update(campos)
        return Notificacao.objects.create(**dados)

    def test_str_mostra_tipo_e_titulo(self):
        self.assertEqual(str(self.nova(titulo='Reunião')), 'Comunicado: Reunião')

    def test_categoria_de_comunicado(self):
        self.assertEqual(self.nova().categoria, 'comunicado')

    def test_categoria_de_estoque_quando_ha_produto(self):
        produto = criar_produto(self.mercado)
        self.assertEqual(self.nova(tipo='use_soon', produto=produto).categoria, 'estoque')

    def test_categoria_de_equipe_quando_nao_ha_produto(self):
        self.assertEqual(self.nova(tipo='tarefa').categoria, 'equipe')

    def test_nao_foi_lida_no_inicio(self):
        usuario = criar_funcionario(self.mercado)
        self.assertFalse(self.nova().foi_lida_por(usuario))

    def test_foi_lida_depois_de_marcada(self):
        usuario = criar_funcionario(self.mercado)
        notificacao = self.nova()
        notificacao.lida_por.add(usuario)
        self.assertTrue(notificacao.foi_lida_por(usuario))

    def test_leitura_de_um_usuario_nao_vale_para_outro(self):
        lido = criar_funcionario(self.mercado, email='a@x.com')
        outro = criar_funcionario(self.mercado, email='b@x.com')
        notificacao = self.nova()
        notificacao.lida_por.add(lido)
        self.assertFalse(notificacao.foi_lida_por(outro))

    def test_publico_padrao_e_toda_a_equipe(self):
        self.assertEqual(self.nova().publico, 'todos')

    def test_mais_recentes_aparecem_primeiro(self):
        antiga = self.nova(titulo='Antiga')
        recente = self.nova(titulo='Recente')
        self.assertEqual(list(Notificacao.objects.all()), [recente, antiga])


class MercadoDoUsuarioTests(BaseTeste):
    def test_devolve_o_mercado_do_perfil(self):
        mercado = criar_mercado()
        self.assertEqual(mercado_do_usuario(criar_gestor(mercado)), mercado)

    def test_usuario_sem_perfil_devolve_none(self):
        sem_perfil = User.objects.create_user(username='admin', password=SENHA)
        self.assertIsNone(mercado_do_usuario(sem_perfil))


class EhGestorTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()

    def test_gestor(self):
        self.assertTrue(eh_gestor(criar_gestor(self.mercado)))

    def test_funcionario_nao_e_gestor(self):
        self.assertFalse(eh_gestor(criar_funcionario(self.mercado)))

    def test_usuario_sem_perfil_nao_e_gestor(self):
        sem_perfil = User.objects.create_superuser(username='root', password=SENHA)
        self.assertFalse(eh_gestor(sem_perfil))


class ContextProcessorNotificacoesTests(BaseTeste):
    def setUp(self):
        self.fabrica = RequestFactory()
        self.mercado = criar_mercado()
        self.usuario = criar_funcionario(self.mercado)

    def contexto_de(self, usuario):
        requisicao = self.fabrica.get('/')
        requisicao.user = usuario
        return notificacoes(requisicao)

    def nova(self, **campos):
        dados = {'tipo': 'comunicado', 'titulo': 'Aviso', 'mensagem': 'Texto', 'mercado': self.mercado}
        dados.update(campos)
        return Notificacao.objects.create(**dados)

    def test_visitante_anonimo_nao_recebe_nada(self):
        self.assertEqual(self.contexto_de(AnonymousUser()), {})

    def test_conta_notificacoes_novas_do_mercado(self):
        self.nova()
        self.nova()
        self.assertEqual(self.contexto_de(self.usuario)['notificacoes_novas'], 2)

    def test_notificacao_lida_nao_conta_como_nova(self):
        self.nova().lida_por.add(self.usuario)
        self.assertEqual(self.contexto_de(self.usuario)['notificacoes_novas'], 0)

    def test_nao_mostra_notificacao_de_outro_mercado(self):
        self.nova(mercado=criar_mercado('Outro'))
        self.assertEqual(self.contexto_de(self.usuario)['notificacoes_novas'], 0)

    def test_mostra_notificacao_enviada_so_para_o_usuario(self):
        self.nova(destinatario=self.usuario)
        self.assertEqual(self.contexto_de(self.usuario)['notificacoes_novas'], 1)

    def test_esconde_notificacao_enviada_para_outra_pessoa(self):
        colega = criar_funcionario(self.mercado, email='colega@x.com')
        self.nova(destinatario=colega)
        self.assertEqual(self.contexto_de(self.usuario)['notificacoes_novas'], 0)

    def test_lista_limitada_a_10_notificacoes(self):
        Notificacao.objects.bulk_create(
            [Notificacao(tipo='comunicado', titulo=f'Aviso {n}', mensagem='x', mercado=self.mercado)
             for n in range(12)]
        )
        self.assertEqual(len(self.contexto_de(self.usuario)['notificacoes']), 10)


# ---------------------------------------------------------------------------
# UNIDADE: formulários de cadastro
# ---------------------------------------------------------------------------

class CadastroFuncionarioFormTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.dados = {
            'nome': 'Maria Souza', 'email': 'maria@mercado.com',
            'senha': SENHA, 'confirmar_senha': SENHA,
            'codigo_mercado': self.mercado.codigo_convite,
        }

    def form(self, **alteracoes):
        return CadastroFuncionarioForm({**self.dados, **alteracoes})

    def test_dados_corretos_sao_validos(self):
        self.assertTrue(self.form().is_valid())

    def test_email_repetido_e_recusado(self):
        criar_funcionario(self.mercado, email='maria@mercado.com')
        self.assertIn('email', self.form().errors)

    def test_email_repetido_com_outra_caixa_tambem_e_recusado(self):
        criar_funcionario(self.mercado, email='maria@mercado.com')
        self.assertIn('email', self.form(email='MARIA@Mercado.com').errors)

    def test_senhas_diferentes_sao_recusadas(self):
        self.assertIn('confirmar_senha', self.form(confirmar_senha='Outra-Senha-9').errors)

    def test_senha_so_com_numeros_e_recusada(self):
        self.assertIn('senha', self.form(senha='83920174', confirmar_senha='83920174').errors)

    def test_senha_curta_e_recusada(self):
        self.assertIn('senha', self.form(senha='Ab1!', confirmar_senha='Ab1!').errors)

    def test_senha_muito_comum_e_recusada(self):
        self.assertIn('senha', self.form(senha='password', confirmar_senha='password').errors)

    def test_senha_parecida_com_o_email_e_recusada(self):
        dados = {'email': 'mariasouza@mercado.com', 'senha': 'mariasouza', 'confirmar_senha': 'mariasouza'}
        self.assertIn('senha', self.form(**dados).errors)

    def test_codigo_de_mercado_inexistente_e_recusado(self):
        self.assertIn('codigo_mercado', self.form(codigo_mercado='ZZZZZZZZ').errors)

    def test_codigo_aceita_minusculas_e_espacos(self):
        codigo = f'  {self.mercado.codigo_convite.lower()} '
        self.assertTrue(self.form(codigo_mercado=codigo).is_valid())

    def test_nome_e_obrigatorio(self):
        self.assertIn('nome', self.form(nome='').errors)

    def test_email_invalido_e_recusado(self):
        self.assertIn('email', self.form(email='isso-nao-e-email').errors)

    def test_finalizar_cria_usuario_comum(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertFalse(formulario.finalizar().is_staff)

    def test_finalizar_cria_perfil_de_funcionario_no_mercado_do_codigo(self):
        formulario = self.form()
        formulario.is_valid()
        perfil = formulario.finalizar().perfil
        self.assertEqual((perfil.papel, perfil.mercado), ('funcionario', self.mercado))

    def test_finalizar_guarda_o_email_em_minusculas_como_usuario(self):
        formulario = self.form(email='Maria@Mercado.COM')
        formulario.is_valid()
        self.assertEqual(formulario.finalizar().username, 'maria@mercado.com')

    def test_finalizar_nao_guarda_a_senha_em_texto_puro(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertNotEqual(formulario.finalizar().password, SENHA)


@override_settings(GESTOR_CODIGO_CONVITE=CODIGO_GESTOR)
class CadastroGestorFormTests(BaseTeste):
    def setUp(self):
        self.dados = {
            'nome': 'Carlos Lima', 'email': 'carlos@mercado.com',
            'senha': SENHA, 'confirmar_senha': SENHA,
            'codigo': CODIGO_GESTOR, 'nome_mercado': 'Mercado Sol', 'cidade_mercado': 'Olinda',
        }

    def form(self, **alteracoes):
        return CadastroGestorForm({**self.dados, **alteracoes})

    def test_dados_corretos_sao_validos(self):
        self.assertTrue(self.form().is_valid())

    def test_codigo_errado_e_recusado(self):
        self.assertIn('codigo', self.form(codigo='errado').errors)

    def test_codigo_vazio_e_recusado(self):
        self.assertIn('codigo', self.form(codigo='').errors)

    @override_settings(GESTOR_CODIGO_CONVITE=None)
    def test_sem_codigo_configurado_o_cadastro_fica_desativado(self):
        self.assertIn('desativado', self.form().errors['codigo'][0])

    def test_nome_do_mercado_e_obrigatorio(self):
        self.assertIn('nome_mercado', self.form(nome_mercado='').errors)

    def test_cidade_e_opcional(self):
        self.assertTrue(self.form(cidade_mercado='').is_valid())

    def test_senhas_diferentes_sao_recusadas(self):
        self.assertIn('confirmar_senha', self.form(confirmar_senha='Outra-Senha-9').errors)

    def test_finalizar_cria_usuario_de_equipe_gestora(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertTrue(formulario.finalizar().is_staff)

    def test_finalizar_cria_o_mercado_com_os_dados_informados(self):
        formulario = self.form()
        formulario.is_valid()
        mercado = formulario.finalizar().perfil.mercado
        self.assertEqual((mercado.nome, mercado.cidade), ('Mercado Sol', 'Olinda'))

    def test_finalizar_cria_perfil_de_gestor(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertEqual(formulario.finalizar().perfil.papel, 'gestor')


# ---------------------------------------------------------------------------
# UNIDADE: formulários de login
# ---------------------------------------------------------------------------

class LoginFuncionarioFormTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.funcionario = criar_funcionario(self.mercado, email='func@mercado.com')

    def form(self, email='func@mercado.com', senha=SENHA):
        return LoginFuncionarioForm({'email': email, 'senha': senha})

    def test_credenciais_corretas_sao_validas(self):
        self.assertTrue(self.form().is_valid())

    def test_finalizar_devolve_o_usuario_autenticado(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertEqual(formulario.finalizar(), self.funcionario)

    def test_email_em_outra_caixa_funciona(self):
        self.assertTrue(self.form(email='FUNC@Mercado.com').is_valid())

    def test_senha_errada_e_recusada(self):
        self.assertIn('incorretos', self.form(senha='errada').non_field_errors()[0])

    def test_email_inexistente_e_recusado(self):
        self.assertIn('incorretos', self.form(email='ninguem@x.com').non_field_errors()[0])

    def test_mensagem_nao_revela_se_o_email_existe(self):
        senha_errada = self.form(senha='errada').non_field_errors()
        email_inexistente = self.form(email='ninguem@x.com').non_field_errors()
        self.assertEqual(senha_errada, email_inexistente)

    def test_conta_de_gestor_e_encaminhada_ao_login_de_gestor(self):
        criar_gestor(self.mercado, email='chefe@mercado.com')
        formulario = self.form(email='chefe@mercado.com')
        self.assertIn('gestor', formulario.non_field_errors()[0])

    def test_conta_inativa_nao_entra(self):
        self.funcionario.is_active = False
        self.funcionario.save()
        self.assertFalse(self.form().is_valid())


class LoginGestorFormTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.gestor = criar_gestor(self.mercado, email='chefe@mercado.com')

    def form(self, usuario='chefe@mercado.com', senha=SENHA):
        return LoginGestorForm({'usuario': usuario, 'senha': senha})

    def test_entra_pelo_nome_de_usuario(self):
        self.assertTrue(self.form(usuario='chefe@mercado.com').is_valid())

    def test_entra_pelo_email_quando_o_usuario_e_diferente(self):
        User.objects.create_user(username='chefao', email='chefao@x.com', password=SENHA, is_staff=True)
        self.assertTrue(self.form(usuario='CHEFAO@x.com').is_valid())

    def test_superusuario_do_admin_entra(self):
        User.objects.create_superuser(username='admin', password=SENHA)
        self.assertTrue(self.form(usuario='admin').is_valid())

    def test_senha_errada_e_recusada(self):
        self.assertIn('incorretos', self.form(senha='errada').non_field_errors()[0])

    def test_usuario_inexistente_e_recusado(self):
        self.assertIn('incorretos', self.form(usuario='fantasma').non_field_errors()[0])

    def test_funcionario_e_encaminhado_ao_login_de_funcionario(self):
        criar_funcionario(self.mercado, email='func@mercado.com')
        formulario = self.form(usuario='func@mercado.com')
        self.assertIn('funcionário', formulario.non_field_errors()[0])

    def test_finalizar_devolve_o_usuario_autenticado(self):
        formulario = self.form()
        formulario.is_valid()
        self.assertEqual(formulario.finalizar(), self.gestor)


# ---------------------------------------------------------------------------
# INTEGRAÇÃO: telas de entrada
# ---------------------------------------------------------------------------

class PaginasPublicasTests(BaseTeste):
    def test_raiz_do_site_redireciona_para_a_pagina_inicial(self):
        self.assertRedirects(self.client.get('/'), reverse('index'), fetch_redirect_response=False)

    def test_pagina_inicial_abre(self):
        self.assertTemplateUsed(self.client.get(reverse('index')), 'index.html')

    def test_login_de_funcionario_abre(self):
        self.assertEqual(self.client.get(reverse('login_funcionario')).status_code, 200)

    def test_cadastro_de_funcionario_abre(self):
        self.assertEqual(self.client.get(reverse('cadastro_funcionario')).status_code, 200)

    def test_login_de_gestor_abre(self):
        self.assertEqual(self.client.get(reverse('login_gestor')).status_code, 200)

    def test_cadastro_de_gestor_abre(self):
        self.assertEqual(self.client.get(reverse('cadastro_gestor')).status_code, 200)

    def test_telas_de_entrada_usam_o_mesmo_template(self):
        self.assertTemplateUsed(self.client.get(reverse('login_gestor')), 'auth.html')

    def test_tema_do_login_de_gestor(self):
        self.assertEqual(self.client.get(reverse('login_gestor')).context['tema'], 'gestor')

    def test_tema_do_login_de_funcionario(self):
        self.assertEqual(self.client.get(reverse('login_funcionario')).context['tema'], 'funcionario')

    def test_url_inexistente_da_404(self):
        self.assertEqual(self.client.get('/nao-existe/').status_code, 404)


class LoginFuncionarioViewTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        criar_funcionario(self.mercado, email='func@mercado.com')
        self.url = reverse('login_funcionario')

    def test_login_correto_leva_ao_estoque(self):
        resposta = self.client.post(self.url, {'email': 'func@mercado.com', 'senha': SENHA})
        self.assertRedirects(resposta, reverse('lista_produtos'))

    def test_login_correto_abre_a_sessao(self):
        self.client.post(self.url, {'email': 'func@mercado.com', 'senha': SENHA})
        self.assertIn('_auth_user_id', self.client.session)

    def test_senha_errada_fica_na_tela_com_erro(self):
        resposta = self.client.post(self.url, {'email': 'func@mercado.com', 'senha': 'errada'})
        self.assertContains(resposta, 'E-mail ou senha incorretos.')

    def test_senha_errada_nao_abre_a_sessao(self):
        self.client.post(self.url, {'email': 'func@mercado.com', 'senha': 'errada'})
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_campos_vazios_mostram_erro_de_obrigatorio(self):
        resposta = self.client.post(self.url, {'email': '', 'senha': ''})
        self.assertEqual(sorted(resposta.context['form'].errors), ['email', 'senha'])


class LoginGestorViewTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        criar_gestor(self.mercado, email='chefe@mercado.com')
        self.url = reverse('login_gestor')

    # gestor -> 'visao-geral'
    # def test_login_correto_leva_ao_estoque(self):
    #     resposta = self.client.post(self.url, {'usuario': 'chefe@mercado.com', 'senha': SENHA})
    #     self.assertRedirects(resposta, reverse('lista_produtos'))

    def test_senha_errada_fica_na_tela_com_erro(self):
        resposta = self.client.post(self.url, {'usuario': 'chefe@mercado.com', 'senha': 'errada'})
        self.assertContains(resposta, 'Usuário ou senha incorretos.')

    def test_funcionario_nao_entra_pelo_login_de_gestor(self):
        criar_funcionario(self.mercado, email='func@mercado.com')
        self.client.post(self.url, {'usuario': 'func@mercado.com', 'senha': SENHA})
        self.assertNotIn('_auth_user_id', self.client.session)


class CadastroFuncionarioViewTests(BaseTeste):
    def setUp(self):
        self.mercado = criar_mercado()
        self.url = reverse('cadastro_funcionario')
        self.dados = {
            'nome': 'Maria Souza', 'email': 'maria@mercado.com',
            'senha': SENHA, 'confirmar_senha': SENHA,
            'codigo_mercado': self.mercado.codigo_convite,
        }

    def test_cadastro_correto_leva_ao_estoque(self):
        self.assertRedirects(self.client.post(self.url, self.dados), reverse('lista_produtos'))

    def test_cadastro_correto_ja_deixa_a_pessoa_logada(self):
        self.client.post(self.url, self.dados)
        self.assertIn('_auth_user_id', self.client.session)

    def test_cadastro_correto_cria_o_usuario(self):
        self.client.post(self.url, self.dados)
        self.assertTrue(User.objects.filter(email='maria@mercado.com').exists())

    def test_codigo_invalido_nao_cria_usuario(self):
        self.client.post(self.url, {**self.dados, 'codigo_mercado': 'ZZZZZZZZ'})
        self.assertEqual(User.objects.count(), 0)

    def test_codigo_invalido_mostra_o_erro_na_tela(self):
        resposta = self.client.post(self.url, {**self.dados, 'codigo_mercado': 'ZZZZZZZZ'})
        self.assertContains(resposta, 'Código de mercado inválido.')

    def test_cadastro_repetido_nao_duplica_usuario(self):
        self.client.post(self.url, self.dados)
        self.client.logout()
        self.client.post(self.url, self.dados)
        self.assertEqual(User.objects.count(), 1)

    def test_senhas_diferentes_nao_criam_usuario(self):
        self.client.post(self.url, {**self.dados, 'confirmar_senha': 'Outra-Senha-9'})
        self.assertEqual(User.objects.count(), 0)

    def test_tela_mostra_o_aviso_do_codigo_do_mercado(self):
        self.assertContains(self.client.get(self.url), 'Você vai precisar do código do mercado')


@override_settings(GESTOR_CODIGO_CONVITE=CODIGO_GESTOR)
class CadastroGestorViewTests(BaseTeste):
    def setUp(self):
        self.url = reverse('cadastro_gestor')
        self.dados = {
            'nome': 'Carlos Lima', 'email': 'carlos@mercado.com',
            'senha': SENHA, 'confirmar_senha': SENHA,
            'codigo': CODIGO_GESTOR, 'nome_mercado': 'Mercado Sol', 'cidade_mercado': 'Olinda',
        }

    # mudou na atualização: redireciona gestor p visão-geral
        # def test_cadastro_correto_leva_ao_estoque(self):
        #     self.assertRedirects(self.client.post(self.url, self.dados), reverse('lista_produtos'))

    def test_cadastro_correto_cria_o_mercado(self):
        self.client.post(self.url, self.dados)
        self.assertTrue(Mercado.objects.filter(nome='Mercado Sol').exists())

    def test_cadastro_correto_cria_gestor_com_perfil(self):
        self.client.post(self.url, self.dados)
        usuario = User.objects.get(email='carlos@mercado.com')
        self.assertEqual((usuario.is_staff, usuario.perfil.papel), (True, 'gestor'))

    def test_codigo_errado_nao_cria_usuario(self):
        self.client.post(self.url, {**self.dados, 'codigo': 'errado'})
        self.assertEqual(User.objects.count(), 0)

    def test_codigo_errado_nao_cria_mercado(self):
        self.client.post(self.url, {**self.dados, 'codigo': 'errado'})
        self.assertEqual(Mercado.objects.count(), 0)

    def test_codigo_errado_mostra_o_erro_na_tela(self):
        resposta = self.client.post(self.url, {**self.dados, 'codigo': 'errado'})
        self.assertContains(resposta, 'Código de acesso inválido.')

    @override_settings(GESTOR_CODIGO_CONVITE=None)
    def test_cadastro_desativado_sem_codigo_configurado(self):
        self.client.post(self.url, self.dados)
        self.assertEqual(User.objects.count(), 0)

    def test_gestor_novo_ve_o_codigo_do_mercado_na_tela_de_equipe(self):
        self.client.post(self.url, self.dados)
        codigo = Mercado.objects.get().codigo_convite
        self.assertContains(self.client.get(reverse('funcionarios')), codigo)


class LogoutTests(BaseTeste):
    def setUp(self):
        self.client.force_login(criar_funcionario(criar_mercado()))

    def test_sair_por_post_encerra_a_sessao(self):
        self.client.post(reverse('sair'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_sair_leva_para_a_pagina_inicial(self):
        resposta = self.client.post(reverse('sair'))
        self.assertRedirects(resposta, reverse('index'))

    def test_sair_por_get_nao_e_permitido(self):
        self.assertEqual(self.client.get(reverse('sair')).status_code, 405)

    def test_sair_por_get_nao_encerra_a_sessao(self):
        self.client.get(reverse('sair'))
        self.assertIn('_auth_user_id', self.client.session)


class ProtecaoDeAcessoTests(BaseTeste):
    """Quem não está logado volta para a página inicial; funcionário não vê a Equipe."""

    def setUp(self):
        self.mercado = criar_mercado()

    def assertVoltaParaInicio(self, url):
        esperado = f"{reverse('index')}?next={url}"
        self.assertRedirects(self.client.get(url), esperado, fetch_redirect_response=False)

    def test_visitante_nao_abre_o_estoque(self):
        self.assertVoltaParaInicio(reverse('lista_produtos'))

    def test_visitante_nao_abre_o_cadastro_de_produto(self):
        self.assertVoltaParaInicio(reverse('adicionar_produto'))

    def test_visitante_nao_abre_o_registro_de_lote(self):
        self.assertVoltaParaInicio(reverse('adicionar_lote', args=[1]))

    def test_visitante_nao_abre_a_equipe(self):
        self.assertVoltaParaInicio(reverse('funcionarios'))

    def test_visitante_nao_consegue_criar_produto_por_post(self):
        self.client.post(reverse('adicionar_produto'), {'nome': 'Invasor'})
        self.assertEqual(Produto.objects.count(), 0)

    def test_funcionario_nao_abre_a_equipe(self):
        self.client.force_login(criar_funcionario(self.mercado))
        resposta = self.client.get(reverse('funcionarios'))
        self.assertRedirects(resposta, reverse('lista_produtos'))

    def test_funcionario_barrado_recebe_aviso(self):
        self.client.force_login(criar_funcionario(self.mercado))
        resposta = self.client.get(reverse('funcionarios'), follow=True)
        self.assertContains(resposta, 'Acesso restrito')

    def test_gestor_abre_a_equipe(self):
        self.client.force_login(criar_gestor(self.mercado))
        self.assertEqual(self.client.get(reverse('funcionarios')).status_code, 200)

    def test_menu_do_gestor_tem_o_link_da_equipe(self):
        self.client.force_login(criar_gestor(self.mercado))
        self.assertContains(self.client.get(reverse('lista_produtos')), reverse('funcionarios'))

    def test_menu_do_funcionario_nao_tem_o_link_da_equipe(self):
        self.client.force_login(criar_funcionario(self.mercado))
        self.assertNotContains(self.client.get(reverse('lista_produtos')), reverse('funcionarios'))
