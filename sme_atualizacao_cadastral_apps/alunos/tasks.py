import logging
from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from config import celery_app
from ..core.helpers.enviar_email import enviar_email_html, enviar_email

env = environ.Env()
log = logging.getLogger(__name__)


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_solicitacao_uniforme(assunto, template, email, contexto):
    log.info(f'Enviando email solicitação para: {email}.')
    return enviar_email_html(
        assunto=assunto,
        template=template,
        contexto=contexto,
        enviar_para=email
    )


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_simples(assunto, mensagem, enviar_para):
    log.info(f'Enviando email solicitação para: {enviar_para}.')
    enviar_email(
        assunto=assunto,
        mensagem=mensagem,
        enviar_para=enviar_para
    )


@celery_app.task(soft_time_limit=1000, time_limit=1200)
def processar_novos_pedidos_mp():
    from .helpers.gerar_csv import gerar_csv_mp
    log.info('Iniciando processo de geração de arquivo e envio por e-mail ao MP.')
    gerar_csv_mp()
    log.info('Processo finalizado.')


@celery_app.task(soft_time_limit=1000, time_limit=1200)
def reenviar_pedidos_ja_enviados_ao_mp():
    from .helpers.gera_csv_registros_ja_enviados import gerar_csv_completo_mp
    log.info('Iniciando processo de geração de arquivo e envio por e-mail ao MP.')
    gerar_csv_completo_mp()
    log.info('Processo finalizado.')


@celery_app.task(soft_time_limit=1000, time_limit=1200)
def processar_pedidos_creditados():
    from ..alunos.helpers.processamento_retorno_mp import ProcessarRetornoService
    log.info(f"Inicia processo de atualização para crédito concedido em massa")
    ProcessarRetornoService.processar_todos_credito_consedido()
    log.info('Processo finalizado.')
