from django.contrib import admin
from .models import Mercado, Perfil, Notificacao

# Register your models here.
@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'criado_em')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mercado', 'papel')
    list_filter = ('papel', 'mercado')

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'publico', 'autor', 'criada_em')
    list_filter = ('tipo', 'publico')
    search_fields = ('titulo', 'mensagem')
    filter_horizontal = ('lida_por',)
    readonly_fields = ('criada_em',)

