from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('<int:produto_id>/lotes/adicionar/', views.adicionar_lote, name='adicionar_lote'),
]
