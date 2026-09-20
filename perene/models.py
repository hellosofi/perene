from django.db import models

# Create your models here.

import datetime
from django.utils import timezone

# class Produto(models.Model):
#     nome = models.CharField(max_length=200, null=False)
#     detalhe = models.TextField(null=False)
#     validade = models.DateField('data', null=True, blank=True)

#     def __str__(self):
#         return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=200, null=False)
    detalhe = models.TextField(null=False)
    validade = models.DateTimeField('data', null=True, blank=True)

    def __str__(self):
        return "[" + str(self.id) + "] " + self.nome
    
    # def status(self):
    #     if self.data_criacao > timezone.now():
    #         return "Vencido"
    #     else:
    #         return "Em análise"

    def string_detalhada(self):
        return "id: " + str(self.id) + "; nome: " + self.nome + "; detalhe: " + self.detalhe + "; validade: " + str(self.validade)