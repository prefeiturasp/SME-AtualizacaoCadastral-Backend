from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import (Aluno, Responsavel, LogConsultaEOL, RetornoMP, LogErroAtualizacaoEOL)
from .forms import LogConsultaEOLForm
from ..utils.actions import export_as_xls
from sme_atualizacao_cadastral_apps.eol_servico.tasks import atualizar_nome_mae_data_nascimento_responsavel


class AlunoInLine(admin.StackedInline):
    model = Aluno
    extra = 0  # Quantidade de linhas que serão exibidas.


class ResponsavelInLine(admin.StackedInline):
    model = Responsavel
    extra = 0  # Quantidade de linhas que serão exibidas.


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    def ultima_alteracao(self, obj):
        return obj.alterado_em.strftime("%d/%m/%Y %H:%M:%S")

    ultima_alteracao.admin_order_field = 'alterado_em'
    ultima_alteracao.short_description = 'Última alteração'

    def celular(self, obj):
        if obj.responsavel.ddd_celular and obj.responsavel.celular:
            return obj.responsavel.ddd_celular + ' ' + obj.responsavel.celular
        else:
            return '-'

    def nome_responsavel(self, obj):
        return obj.responsavel.nome

    nome_responsavel.short_descriptions = 'Nome do Responsavel'

    def cpf_responsavel(self, obj):
        return obj.responsavel.cpf

    cpf_responsavel.short_descriptions = 'CPF do Responsavel'

    list_display = ('nome', 'codigo_eol', 'data_nascimento', 'nome_responsavel',
                    'cpf_responsavel', 'celular')
    readonly_fields = ('responsavel',)
    ordering = ('-alterado_em',)
    search_fields = ('codigo_eol', 'nome', 'responsavel__cpf', 'responsavel__nome')
    list_filter = ('responsavel__status',)


class TemCelularFilter(SimpleListFilter):
    title = 'tem_celular'
    parameter_name = 'celular'

    def lookups(self, request, model_admin):
        return [('Sim', 'Sim'), ('Não', 'Não')]

    def queryset(self, request, queryset):
        if self.value() == 'Sim':
            return queryset.filter(celular__isnull=False)
        elif self.value() == 'Não':
            return queryset.filter(celular__isnull=True)
        else:
            return queryset


class TemEmailFilter(SimpleListFilter):
    title = 'tem_email'
    parameter_name = 'email'

    def lookups(self, request, model_admin):
        return [('Sim', 'Sim'), ('Não', 'Não')]

    def queryset(self, request, queryset):
        if self.value() == 'Sim':
            return queryset.filter(email__isnull=False)
        elif self.value() == 'Não':
            return queryset.filter(email__isnull=True)
        else:
            return queryset


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    inlines = [AlunoInLine]

    def ultima_alteracao(self, obj):
        return obj.alterado_em.strftime("%d/%m/%Y %H:%M:%S")

    ultima_alteracao.admin_order_field = 'alterado_em'
    ultima_alteracao.short_description = 'Última alteração'

    def get_celular(self, obj):
        if obj.ddd_celular and obj.celular:
            return obj.ddd_celular + ' ' + obj.celular
        else:
            return '-'

    def enviar_emails(self, request, queryset):
        for responsavel in queryset.all():
            responsavel.enviar_email()
        self.message_user(request, 'E-mails enviados com sucesso.')

    enviar_emails.short_description = 'Enviar email para responsaveis'

    def salvar_no_eol(self, request, queryset):
        queryset = queryset.filter(status__in=['ATUALIZADO_VALIDO', 'PENDENCIA_RESOLVIDA'])
        for responsavel in queryset:
            responsavel.salvar_no_eol()
        self.message_user(request, 'Registros enviados para processamento no celery.')

    salvar_no_eol.short_description = 'Atualizar Responsaveis na base EOL'

    def atualizar_dados_responsaveis(self, request, _):
        atualizar_nome_mae_data_nascimento_responsavel.delay()
        self.message_user(request, "Os dados estão sendo atualizados.")
    
    atualizar_dados_responsaveis.short_description = "Atualiza nome da mãe e data nascimento responsável."


    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'enviar_emails' in actions:
                del actions['enviar_emails']
        return actions

    list_display = ('nome', 'cpf', 'codigo_eol_aluno', 'data_nascimento', 'vinculo', 'nome_mae', 'get_celular', 'email',
                    'status', 'criado_em')
    ordering = ('-alterado_em',)
    search_fields = ('uuid', 'cpf', 'nome', 'codigo_eol_aluno')
    list_filter = ('status', TemCelularFilter, TemEmailFilter)
    actions = ['enviar_emails', 'salvar_no_eol', export_as_xls, 'atualizar_dados_responsaveis']


@admin.register(LogConsultaEOL)
class LogConsultaEOLAdmin(admin.ModelAdmin):
    form = LogConsultaEOLForm
    list_display = ('codigo_eol', 'criado_em',)
    search_fields = ('codigo_eol',)
    readonly_fields = ('criado_em',)
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    fields = ('codigo_eol', 'criado_em', 'json')


@admin.register(RetornoMP)
class RetornoMPAdmin(admin.ModelAdmin):
    def get_nome_responsavel(self, obj):
        if obj.responsavel:
            return obj.responsavel.nome
        else:
            return '-'
    get_nome_responsavel.short_description = 'Nome Responsável'

    list_display = ('get_nome_responsavel', 'cpf', 'codigo_eol', 'status', 'data_ocorrencia', 'mensagem', 'alterado_em',
                    'registro_processado', 'ativo')
    search_fields = ('codigo_eol', 'cpf')
    readonly_fields = ('responsavel', 'cpf', 'codigo_eol', 'status', 'mensagem', 'data_ocorrencia', 'criado_em', 'alterado_em',
                      'registro_processado')
    list_filter = ('registro_processado', 'status')


@admin.register(LogErroAtualizacaoEOL)
class LogErroAtualizacaoEOLAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'codigo_eol', 'criado_em',)
    search_fields = ('nome', 'cpf', 'codigo_eol',)
    readonly_fields = ('criado_em',)
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    fields = ('nome', 'cpf', 'codigo_eol', 'criado_em', 'resolvido', 'erro')
