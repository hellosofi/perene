from django.db import models

# Create your models here.

# provisório - - - -
class Funcionario(models.Model):
    nome = models.CharField(max_length=200)
    iniciais = models.CharField(max_length=4)
    cargo = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
# - - - - - - - - -

class Tarefa(models.Model):
    titulo = models.CharField(max_length=200)
    area = models.CharField(max_length=100, blank=True)
    
    responsavel = models.ForeignKey(
        Funcionario, null=True, blank=True, on_delete=models.SET_NULL, related_name='tarefas'
    )
    
    horario = models.TimeField(null=True, blank=True)
    concluida = models.BooleanField(default=False) # < ------------ 

    def __str__(self):
        return self.titulo
