import logging
from django.core import validators
from django.db import models

from sme_atualizacao_cadastral_apps.core.models_abstracts import ModeloBase
from ..tasks import enviar_email_solicitacao_uniforme
from ...eol_servico.tasks import atualizar_responsavel_no_eol

from .validators import phone_validation, cpf_validation

log = logging.getLogger(__name__)


class Responsavel(ModeloBase):
    # Status Choice
    STATUS_ATUALIZADO_EOL = 'ATUALIZADO_EOL'
    STATUS_ATUALIZADO_VALIDO = 'ATUALIZADO_VALIDO'
    STATUS_DIVERGENTE = 'DIVERGENTE'
    STATUS_DESATUALIZADO = 'DESATUALIZADO'
    STATUS_PENDENCIA_RESOLVIDA = 'PENDENCIA_RESOLVIDA'
    STATUS_CREDITO_CONCEDIDO = 'CREDITO_CONCEDIDO'
    STATUS_INCONSISTENCIA_RESOLVIDA = 'INCONSISTENCIA_RESOLVIDA'
    STATUS_CPF_INVALIDO = 'CPF_INVALIDO'
    STATUS_EMAIL_INVALIDO = 'EMAIL_INVALIDO'
    STATUS_MULTIPLOS_EMAILS = 'MULTIPLOS_EMAILS'

    STATUS_NOMES = {
        STATUS_ATUALIZADO_EOL: 'Cadastro Atualizado no EOL',
        STATUS_ATUALIZADO_VALIDO: 'Cadastro Atualizado e validado',
        STATUS_DIVERGENTE: 'Cadastro Divergente',
        STATUS_DESATUALIZADO: 'Cadastro Desatualizado',
        STATUS_PENDENCIA_RESOLVIDA: 'Cadastro com Pendência Resolvida',
        STATUS_CREDITO_CONCEDIDO: 'Cadastro com Crédito Concedido',
        STATUS_INCONSISTENCIA_RESOLVIDA: 'Cadastro com inconsistência resolvida',
        STATUS_CPF_INVALIDO: 'Cadastro com CPF inválido',
        STATUS_EMAIL_INVALIDO: 'Cadastro com e-mail inválido',
        STATUS_MULTIPLOS_EMAILS: 'Cadastro com mais de um e-mail cadastrado',
    }

    STATUS_CHOICES = (
        (STATUS_ATUALIZADO_EOL, STATUS_NOMES[STATUS_ATUALIZADO_EOL]),
        (STATUS_ATUALIZADO_VALIDO, STATUS_NOMES[STATUS_ATUALIZADO_VALIDO]),
        (STATUS_DIVERGENTE, STATUS_NOMES[STATUS_DIVERGENTE]),
        (STATUS_DESATUALIZADO, STATUS_NOMES[STATUS_DESATUALIZADO]),
        (STATUS_PENDENCIA_RESOLVIDA, STATUS_NOMES[STATUS_PENDENCIA_RESOLVIDA]),
        (STATUS_CREDITO_CONCEDIDO, STATUS_NOMES[STATUS_CREDITO_CONCEDIDO]),
        (STATUS_INCONSISTENCIA_RESOLVIDA, STATUS_NOMES[STATUS_INCONSISTENCIA_RESOLVIDA]),
        (STATUS_CPF_INVALIDO, STATUS_NOMES[STATUS_CPF_INVALIDO]),
        (STATUS_EMAIL_INVALIDO, STATUS_NOMES[STATUS_EMAIL_INVALIDO]),
        (STATUS_MULTIPLOS_EMAILS, STATUS_NOMES[STATUS_MULTIPLOS_EMAILS]),
    )

    # Vinculo Choice
    VINCULO_MAE = 1
    VINCULO_PAI = 2
    VINCULO_RESPONSAVEL_LEGAL = 3
    VINCULO_ALUNO_MAIOR_IDADE = 4

    VINCULO_NOMES = {
        VINCULO_MAE: 'Mãe',
        VINCULO_PAI: 'Pai',
        VINCULO_RESPONSAVEL_LEGAL: 'Responsável Legal',
        VINCULO_ALUNO_MAIOR_IDADE: 'Aluno Maior de Idade',
    }

    VINCULO_CHOICES = (
        (VINCULO_MAE, VINCULO_NOMES[VINCULO_MAE]),
        (VINCULO_PAI, VINCULO_NOMES[VINCULO_PAI]),
        (VINCULO_RESPONSAVEL_LEGAL, VINCULO_NOMES[VINCULO_RESPONSAVEL_LEGAL]),
        (VINCULO_ALUNO_MAIOR_IDADE, VINCULO_NOMES[VINCULO_ALUNO_MAIOR_IDADE]),
    )

    vinculo = models.IntegerField(
        'Vínculo',
        choices=VINCULO_CHOICES,
        default=VINCULO_RESPONSAVEL_LEGAL
    )

    codigo_eol_aluno = models.CharField("Código EOL do Aluno", max_length=10, blank=True, null=True)

    nome = models.CharField("Nome do Responsável", max_length=255, blank=True, null=True)

    cpf = models.CharField(
        "CPF", max_length=11, blank=True, null=True, validators=[cpf_validation])

    email = models.CharField(
        "E-mail", max_length=255, validators=[validators.EmailValidator()], blank=True, null=True
    )

    nao_possui_email = models.BooleanField(default=False)

    ddd_celular = models.CharField("DDD Celular", max_length=4, blank=True, null=True)

    celular = models.CharField("Número Celular", validators=[phone_validation], max_length=9, blank=True, null=True)

    nao_possui_celular = models.BooleanField(default=False)

    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)

    nome_mae = models.CharField("Nome da Mãe do Responsável", max_length=255, blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ATUALIZADO_VALIDO
    )

    pendencia_resolvida = models.BooleanField(default=False)

    enviado_para_mercado_pago = models.BooleanField(default=False)

    data_envio_mercado_pago = models.DateField("Data de Envio Mercado Pago", blank=True, null=True)
    responsavel_alterado = models.BooleanField(default=False)

    def enviar_email(self):
        if self.email:
            nome_aluno = self.alunos.nome
            if self.status == 'DIVERGENTE':
                log.info(f'Enviando email divergencia para: {self.email}.')
                enviar_email_solicitacao_uniforme.delay(
                    'Divergência nos dados informados', 'email_divergencia_cpf', self.email, {'nome': nome_aluno,
                                                                                              'id': self.id})
            else:
                log.info(f'Enviando email confirmação para: {self.email}.')
                enviar_email_solicitacao_uniforme.delay(
                    'Obrigado por solicitar o uniforme escolar', 'email_confirmacao_pedido', self.email,
                    {'nome': nome_aluno, 'id': self.id})
        else:
            log.info('Não possui e-mail para envio')

    def salvar_no_eol(self):
        tipo_turno_celular = '1' if self.celular else ''
        data_nascimento = str(self.data_nascimento).replace('-', '')
        log.info(f"Atualizando informações do responsavel pelo aluno: {self.codigo_eol_aluno} no eol")
        atualizar_responsavel_no_eol.delay(self.codigo_eol_aluno, str(self.vinculo), self.nome.upper(), self.cpf,
                                           self.ddd_celular, self.celular, self.email, self.nome_mae.upper(),
                                           data_nascimento, tipo_turno_celular)

    def __str__(self):
        return f"{self.nome} - Cod. EOL Aluno: {self.codigo_eol_aluno}"

    class Meta:
        verbose_name = "Responsavel"
        verbose_name_plural = "Responsaveis"
