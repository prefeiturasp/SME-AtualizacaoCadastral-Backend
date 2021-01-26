from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from sme_atualizacao_cadastral_apps.alunos.models import Responsavel
from sme_atualizacao_cadastral_apps.core.models_abstracts import ModeloBase
from .validators import cpf_validation

from sme_atualizacao_cadastral_apps.alunos.helpers.processamento_retorno_mp import ProcessarRetornoService


class RetornoMP(ModeloBase):
    # Status Choice
    STATUS_MULTIPLOS_EMAILS = 5
    STATUS_MULTIPLOS_CPFS_MESMO_EOL = 7
    STATUS_CREDITADO = 9
    STATUS_EMAIL_INVALIDO = 10
    STATUS_CPF_INVALIDO = 11

    STATUS_NOMES = {
        STATUS_MULTIPLOS_EMAILS: 'Responsável com mais de um e-mail informado',
        STATUS_MULTIPLOS_CPFS_MESMO_EOL: 'Crédito já liberado para outro CPF',
        STATUS_CREDITADO: 'Crédito Concedido',
        STATUS_EMAIL_INVALIDO: 'E-mail Inválido',
        STATUS_CPF_INVALIDO: 'CPF Inválido',
    }

    STATUS_CHOICES = (
        (STATUS_MULTIPLOS_EMAILS, STATUS_NOMES[STATUS_MULTIPLOS_EMAILS]),
        (STATUS_MULTIPLOS_CPFS_MESMO_EOL, STATUS_NOMES[STATUS_MULTIPLOS_CPFS_MESMO_EOL]),
        (STATUS_CREDITADO, STATUS_NOMES[STATUS_CREDITADO]),
        (STATUS_EMAIL_INVALIDO, STATUS_NOMES[STATUS_EMAIL_INVALIDO]),
        (STATUS_CPF_INVALIDO, STATUS_NOMES[STATUS_CPF_INVALIDO]),
    )

    codigo_eol = models.CharField(
        "Código EOL do Aluno", max_length=7, validators=[validators.MinLengthValidator(7)])
    cpf = models.CharField(
        "CPF", max_length=11, blank=True, null=True, validators=[cpf_validation])
    status = models.IntegerField(
        'Status',
        choices=STATUS_CHOICES
    )
    mensagem = models.CharField("Mensagem", max_length=255, blank=True, null=True)
    data_ocorrencia = models.DateField("Data de Ocorrencia no MP", blank=True, null=True)
    registro_processado = models.BooleanField("Registro Processado?", default=False)
    ativo = models.BooleanField("Está ativo?", default=True)
    responsavel = models.ForeignKey(Responsavel, on_delete=models.PROTECT,
                                    blank=True, null=True, related_name='retornos')

    def __str__(self):
        return f'{self.cpf} - {self.codigo_eol}'

    class Meta:
        verbose_name = "Retorno do Mercado Pago"
        verbose_name_plural = "Retornos do Mercado Pago"


@receiver(post_save, sender=RetornoMP)
def retorno_post_save(instance, created, **kwargs):
    if created and instance:
        if instance.status == RetornoMP.STATUS_CREDITADO:
            Responsavel.objects.filter(id=instance.responsavel.id).update(status=Responsavel.STATUS_CREDITO_CONCEDIDO)
            instance.registro_processado = True
            instance.save()
        elif instance.status == RetornoMP.STATUS_CPF_INVALIDO:
            ProcessarRetornoService.cpf_invalido(instance.responsavel.id)
            instance.registro_processado = True
            instance.save()
        elif instance.status == RetornoMP.STATUS_EMAIL_INVALIDO:
            Responsavel.objects.filter(id=instance.responsavel.id).update(status=Responsavel.STATUS_EMAIL_INVALIDO)
            instance.registro_processado = True
            instance.save()
        elif instance.status == RetornoMP.STATUS_MULTIPLOS_EMAILS:
            ProcessarRetornoService.multiplos_emails(instance.responsavel.id)
            instance.registro_processado = True
            instance.save()
