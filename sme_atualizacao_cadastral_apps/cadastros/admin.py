
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path

from .models import BaseCadastro, LogProcessamentoPlanilha, PlanilhaSituacao


@admin.register(PlanilhaSituacao)
class PlanilhaSituacaoAdmin(admin.ModelAdmin):
    change_list_template = "cadastro_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('processar_planilha/', self.processar_planilha),
        ]
        return my_urls + urls

    def arquivo_nome(self, obj):
        return f'{obj.arquivo.name.split("/")[-1]}'

    arquivo_nome.short_descriptions = 'arquivo'

    def processar_planilha(self, request):
        planilha = self.model.objects.last()
        if not planilha.extraido:
            planilha.processar_planilha()
            self.message_user(request, f'Processamento da planilha {planilha.arquivo.name.split("/")[-1]} '
                                       f'foi iniciado. Esta tarefa pode demorar um pouco.')
        else:
            self.message_user(request, f'A planilha {planilha.arquivo.name.split("/")[-1]} '
                                       f'não pode ser processada novamente.', level=messages.ERROR)
        return HttpResponseRedirect("../")

    processar_planilha.short_description = 'Processar ultima planilha cadastrada'

    list_display = ('arquivo_nome', 'criado_em', 'data_corte_planilha', 'data_corte_lote', 'extraido')
    ordering = ('-criado_em',)


@admin.register(BaseCadastro)
class BaseCadastroAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'situacao')
    readonly_fields = ('cpf', 'situacao')


@admin.register(LogProcessamentoPlanilha)
class LogProcessamentoPlanilhaAdmin(admin.ModelAdmin):

    list_display = ('arquivo', 'criado_em', 'status')
    readonly_fields = ('arquivo', 'criado_em', 'status', 'msg_retorno')
