from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('adicionar/', views.Add_produto.as_view(), name="inserir_produto"),
    path('produtos/', views.Produto_view.as_view(), name="lista_produtos")


    # # ex: /forum/
    # path("", views.MainView.as_view(), name="index"),
    # # ex: /forum/5/
    # path("<int:pergunta_id>/", views.PerguntaView.as_view(), name="detalhe"),
    # # ex: /forum/5/voto/
    # path("<int:resposta_id>/voto/", views.VotoView.as_view(), name="voto"),
    # # ex: /forum/inserir/
    # path("inserir/", views.InserirPerguntaView.as_view(), name="inserir_pergunta"),
    # # ex: /forum/5/resposta/
    # path("<int:pergunta_id>/resposta/",
    #      views.InserirRespostaView.as_view(), name="inserir_resposta"),
]