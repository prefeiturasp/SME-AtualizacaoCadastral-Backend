from django.core import validators
from django.db import models

from ..models_abstracts import ModeloBase


class EmailMercadoPago(ModeloBase):
    email = models.CharField('Email', max_length=255, validators=[validators.EmailValidator()])

    class Meta:
        verbose_name = "E-mail mercado pago"
        verbose_name_plural = "E-mail mercado pago"
