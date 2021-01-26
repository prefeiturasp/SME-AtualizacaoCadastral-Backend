from django.db import models

from ..models_abstracts import ModeloBase


class ListaPalavrasBloqueadas(ModeloBase):
    palavra = models.CharField("Palavra", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.palavra

    class Meta:
        verbose_name = "Lista palavra bloqueada"
        verbose_name_plural = "Lista palavras bloqueadas"
