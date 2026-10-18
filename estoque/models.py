from django.db import models
# Create your models here.

# novo banco de dados
class Produto(models.Model):
    
    STATUS_CHOICES = [
        ('all_good', 'Tudo certo'),
        ('use_soon', 'Vencimento próximo'),
        ('low_stock', 'Estoque baixo'),
        ('damaged', 'Danificado'),
        ('surplus', 'Excedente'),
        ('undocumented', 'Não cadastrado'),
    ]

    # classes css
    STATUS_CSS = {
        'all_good': 'etiqueta-ok',
        'use_soon': 'etiqueta-vencendo',
        'low_stock': 'etiqueta-baixo',
        'damaged': 'etiqueta-danificado',
        'surplus': 'etiqueta-excedente',
        'undocumented': 'etiqueta-nao-cadastrado',
    }

    # informações sobre produto
    nome = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    detalhe = models.TextField(blank=True)
    quantidade = models.IntegerField(default=0)
    unidade = models.CharField(max_length=50, blank=True)
    validade = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='all_good')

    def __str__(self):
        return f'[{self.codigo}] {self.nome}'


    # p chamar os métodos

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    # chamar classe
    @property
    def status_css(self):
        return self.STATUS_CSS.get(self.status, '')

    # verificador
    @property
    def tem_ocorrencia(self):
        return self.status != 'all_good'
