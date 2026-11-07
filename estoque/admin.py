from django.contrib import admin

from django.contrib import admin
from .models import Produto, Lote

class LoteInline(admin.TabularInline):
    model = Lote
    extra = 1

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'categoria', 'quantidade_total')
    inlines = [LoteInline]
