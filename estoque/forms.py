from django import forms
from .models import Lote, Produto

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade', 'validade', 'local', 'observacao', 'avariado']
        labels = {
            'local': 'Local no mercado',
            'observacao': 'Observação (opcional)',
            'avariado': 'Lote avariado',
        }
        help_texts = {
            'quantidade': 'Na unidade do cadastro do produto.',
        }
        widgets = {
            'validade': forms.DateInput(attrs={'type': 'date'}),
            'local': forms.TextInput(attrs={'placeholder': 'Ex.: Balcão refrigerado 2'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex.: embalagem amassada, chegou com atraso…'}),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'codigo', 'categoria', 'unidade', 'estoque_minimo', 'dias_alerta', 'detalhe']
        labels = {
            'codigo': 'Código',
            'estoque_minimo': 'Estoque mínimo',
            'dias_alerta': 'Avisar antes de vencer (dias)',
            'detalhe': 'Detalhe (opcional)',
        }
        help_texts = {
            'unidade': 'Por exemplo: un. ou kg.',
            'estoque_minimo': 'Abaixo disso, o produto entra em Atenção. Use 0 para não avisar.',
            'dias_alerta': 'Prazo para o lote entrar em Atenção.',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Iogurte natural 170 g'}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Ex.: 7891000100103'}),
            'categoria': forms.TextInput(attrs={'placeholder': 'Ex.: Frios e laticínios'}),
            'unidade': forms.TextInput(attrs={'placeholder': 'un.'}),
            'detalhe': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex.: marca, sabor, fornecedor habitual…'}),
        }
