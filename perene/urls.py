from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("funcionario/entrar/", views.LoginFuncionario.as_view(), name="login_funcionario"),
    path("funcionario/cadastro/", views.CadastroFuncionario.as_view(), name="cadastro_funcionario"),
    path("gestor/entrar/", views.LoginGestor.as_view(), name="login_gestor"),
    path("gestor/cadastro/", views.CadastroGestor.as_view(), name="cadastro_gestor"),
    path("sair/", LogoutView.as_view(), name="sair"),
    path("notificacoes/", views.notificacoes, name="notificacoes"),
    path("notificacoes/lidas/", views.marcar_notificacoes_lidas, name="marcar_notificacoes_lidas"),
    path("notificacoes/comunicado/", views.enviar_comunicado, name="enviar_comunicado"),
    # path('adicionar/', views.Add_produto.as_view(), name="inserir_produto"),  # saiu do perene --> estoque
    # path('produtos/', views.Produto_view.as_view(), name="lista_produtos")    # saiu do perene --> estoque
]