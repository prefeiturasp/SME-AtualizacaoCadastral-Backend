from django.db import models

from ..models_abstracts import ModeloBase


class ListaEmail(ModeloBase):
    email = models.CharField('Email', max_length=255)

    class Meta:
        verbose_name = "Lista de Email (SME)"
        verbose_name_plural = "Lista de Emails (SME)"
