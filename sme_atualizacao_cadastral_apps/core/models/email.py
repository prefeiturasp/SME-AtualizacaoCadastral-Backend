from django.db import models

from ..models_abstracts import ModeloBase


class Email(ModeloBase):
    enviado = models.BooleanField("Enviado?", default=False)
    enviar_para = models.CharField("Enviar Para", max_length=255, blank=True, null=True)
    assunto = models.CharField("Assunto", max_length=255, blank=True, null=True)
    body = models.TextField("Enviar Para", blank=True, null=True)

    class Meta:
        verbose_name = "Log e-mail enviado (Atualização Cadastral)"
        verbose_name_plural = "Log e-mails enviados (Atualização Cadastral)"


class LogEmailMercadoPago(ModeloBase):
    enviado = models.BooleanField("Enviado?", default=False)
    enviar_para = models.CharField("Enviar Para", max_length=255, blank=True, null=True)
    assunto = models.CharField("Assunto", max_length=255, blank=True, null=True)
    mensagem = models.TextField("Mensagem", blank=True, null=True)
    csv = models.CharField("Arquivo CSV", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Log e-mail enviado (Mercado Pago)"
        verbose_name_plural = "Log e-mails enviados (Mercado Pago)"
