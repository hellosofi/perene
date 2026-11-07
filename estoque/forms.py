from django import forms
from .models import Lote

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
