from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('adicionar/', views.Add_produto.as_view(), name="inserir_produto"),
    path('produtos/', views.Produto_view.as_view(), name="lista_produtos")
]