from django import forms

from .models import Tarefa


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'area', 'responsavel', 'horario']
        labels = {
            'titulo': 'O que precisa ser feito',
            'area': 'Área (opcional)',
            'responsavel': 'Responsável',
            'horario': 'Até que horas (opcional)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex.: Conferir validade do balcão de frios'}),
            'area': forms.TextInput(attrs={'placeholder': 'Ex.: Frios e laticínios'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsavel'].empty_label = 'Sem responsável'
