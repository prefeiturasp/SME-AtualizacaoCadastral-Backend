from django.contrib import admin
from django.utils.html import format_html

from .models import ListaPalavrasBloqueadas, Email, ListaEmail, EmailMercadoPago, LogEmailMercadoPago


@admin.register(ListaPalavrasBloqueadas)
class ListaPalavrasBloqueadasAdmin(admin.ModelAdmin):
    list_display = ('palavra', 'criado_em',)
    search_fields = ('palavra',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('enviar_para', 'criado_em', 'assunto', 'enviado')
    search_fields = ('enviar_para', 'criado_em', 'enviado')
    list_filter = ('enviado',)


@admin.register(LogEmailMercadoPago)
class LogEmailMercadoPagoAdmin(admin.ModelAdmin):

    def csv_url(self, obj):
        return format_html('<a href="{0}" >{0}</a>&nbsp;', obj.csv)

    list_display = ('criado_em', 'enviar_para', 'assunto', 'enviado', 'csv_url')
    search_fields = ('assunto', 'criado_em')
    list_filter = ('enviado',)
    ordering = ('-criado_em',)
    readonly_fields = ('enviar_para', 'assunto', 'mensagem', 'csv_url', )
    exclude = ('csv',)


@admin.register(ListaEmail)
class ListaEmailAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)


@admin.register(EmailMercadoPago)
class EmailMercadoPagoAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not EmailMercadoPago.objects.exists()

    list_display = ('email',)
    search_fields = ('email',)
