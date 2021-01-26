from django.core import validators
from django.db import models
from django.contrib.postgres.fields import JSONField
from sme_atualizacao_cadastral_apps.core.models_abstracts import ModeloBase
from .validators import cpf_validation


class LogErroAtualizacaoEOL(ModeloBase):
    codigo_eol = models.CharField(
        "Código EOL do Aluno", max_length=7, validators=[validators.MinLengthValidator(7)])
    cpf = models.CharField(
        "CPF do Responsável", max_length=11, blank=True, null=True, validators=[cpf_validation])
    nome = models.CharField("Nome do Responsável", max_length=255, blank=True, null=True)
    resolvido = models.BooleanField("Erro Resolvido?", default=False)
    erro = JSONField('Erro', blank=True, default=dict)

    def __str__(self):
        return f"{self.nome} - {self.codigo_eol} - {self.cpf}"

    class Meta:
        verbose_name = "Log de Erro na atualização no EOL"
        verbose_name_plural = "Logs de Erros em Atualizações no EOL"
