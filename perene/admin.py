from django.contrib import admin
from .models import Notificacao

# Register your models here.

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'publico', 'autor', 'criada_em')
    list_filter = ('tipo', 'publico')
    search_fields = ('titulo', 'mensagem')
    filter_horizontal = ('lida_por',)
    readonly_fields = ('criada_em',)

