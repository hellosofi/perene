from django import forms
from .models import Lote

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade', 'validade', 'local', 'observacao', 'avariado']
        widgets = {'validade': forms.DateInput(attrs={'type': 'date'})}