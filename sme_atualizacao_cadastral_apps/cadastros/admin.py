
from django.contrib import admin

from .models import BaseCadastro, PlanilhaSituacao


@admin.register(PlanilhaSituacao)
class PlanilhaSituacaoAdmin(admin.ModelAdmin):

    def arquivo_nome(self, obj):
        return f'{obj.arquivo.name.split("/")[-1]}'

    arquivo_nome.short_descriptions = 'arquivo'

    list_display = ('arquivo_nome', 'criado_em', 'data_corte_planilha', 'data_corte_lote', 'extraido')
    ordering = ('-criado_em',)


@admin.register(BaseCadastro)
class BaseCadastroAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'situacao')
    readonly_fields = ('cpf', 'situacao')
