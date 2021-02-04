from django.db import models

from sme_atualizacao_cadastral_apps.core.models_abstracts import ModeloBase
from .responsavel import Responsavel


class Aluno(ModeloBase):
    codigo_eol = models.CharField(
        "Código EOL do Aluno", max_length=10, unique=True)
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    nome = models.CharField("Nome do Aluno", max_length=255, blank=True, null=True)
    codigo_escola = models.CharField("Código EOL da Escola", max_length=10, blank=True, null=True)
    codigo_dre = models.CharField("Código EOL da DRE", max_length=10, blank=True, null=True)
    atualizado_na_escola = models.BooleanField("Atualizado na Escola", default=False)
    servidor = models.CharField("RF do Servidor", max_length=10, blank=True, null=True)
    responsavel = models.OneToOneField(Responsavel, on_delete=models.CASCADE,
                                       blank=True, null=True, related_name='alunos')

    def __str__(self):
        return f"{self.codigo_eol} - {self.nome}"

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
