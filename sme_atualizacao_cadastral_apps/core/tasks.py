import datetime
from datetime import timedelta
from smtplib import SMTPServerDisconnected

from celery.schedules import crontab
from celery.task import periodic_task
from config import celery_app

from sme_atualizacao_cadastral_apps.alunos.models import Responsavel
from sme_atualizacao_cadastral_apps.core.helpers.enviar_email import enviar_email_html, enviar_email_mp
from sme_atualizacao_cadastral_apps.core.models import Email, LogEmailMercadoPago


@celery_app.task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_emails_engasgados():
    emails = Email.objects.filter(enviar_para__isnull=False, enviado=False, criado_em__gt=datetime.date(2020, 10, 29))

    for email in emails:
        contexto = {'id': email.id}
        enviar_email_html(assunto=email.assunto, template=None, contexto=contexto, enviar_para=email.enviar_para,
                          html_salvo=email.body, lista_emails=None)


def enviar_emails_cadastros_divergentes():
    responsaveis = Responsavel.objects.filter(status="DIVERGENTE", email__isnull=False)
    for responsavel in responsaveis:
        responsavel.enviar_email()


@celery_app.task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_emails_engasgados_mp():
    emails = LogEmailMercadoPago.objects.filter(enviar_para__isnull=False, enviado=False)

    for email in emails:
        enviar_email_mp(assunto=email.assunto, mensagem=email.mensagem, csv=email.csv)
