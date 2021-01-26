from django.core import validators
from django.db import models
from django.contrib.postgres.fields import JSONField
from sme_atualizacao_cadastral_apps.core.models_abstracts import ModeloBase


class LogConsultaEOL(ModeloBase):
    codigo_eol = models.CharField(
        "Código EOL do Aluno", max_length=7, validators=[validators.MinLengthValidator(7)])
    json = JSONField('Log', blank=True, default=dict)

    def __str__(self):
        return self.codigo_eol

    class Meta:
        verbose_name = "Log Consulta EOL"
        verbose_name_plural = "Logs Consultas EOL"
