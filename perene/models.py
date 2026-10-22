# import
from django.db import models
from django.conf import settings 

from estoque.models import Produto
from funcionarios.models import Tarefa

# Create your models here.

class Notificacao(models.Model):

    TIPO_CHOICES = [
        ('Estoque', [
            ('use_soon', 'Vencimento próximo'),
            ('low_stock', 'Estoque baixo'),
            ('damaged', 'Lote danificado'),
            ('undocumented', 'Não cadastrado'),
        ]),

        ('Equipe', [
            ('tarefa', 'Tarefa'),
        ]),
        
        # escrita à mão pelo gestor
        ('Comunicação', [
            ('comunicado', 'Comunicado'),
        ]),
    ]

    ## repensar...
    PUBLICO_CHOICES = [
        ('todos', 'Toda a equipe'),
        ('manha', 'Turno da manhã'),
        ('tarde', 'Turno da tarde'),
        ('noite', 'Turno da noite'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=120)
    mensagem = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    lida_por = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='notificacoes_lidas'
    )
    publico = models.CharField(max_length=10, choices=PUBLICO_CHOICES, default='todos')


    # origem
    produto = models.ForeignKey(
        Produto, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes'
    )

    tarefa = models.ForeignKey(
        Tarefa, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes'
    )

    # enviado para:
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
        related_name='notificacoes_recebidas'
    )

    # criada por:  
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='notificacoes_enviadas'
    )

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo}'

    @property
    def categoria(self):
        if self.tipo == 'comunicado':
            return 'comunicado'
        return 'estoque' if self.produto_id else 'equipe'

    def foi_lida_por(self, usuario):
        return self.lida_por.filter(pk=usuario.pk).exists()