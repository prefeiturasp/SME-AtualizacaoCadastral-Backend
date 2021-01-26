import logging

import environ
from des.models import DynamicEmailConfiguration
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string

from sme_atualizacao_cadastral_apps.core.models import Email, ListaEmail, EmailMercadoPago, LogEmailMercadoPago

logger = logging.getLogger(__name__)

env = environ.Env()


def enviar_email(assunto, mensagem, enviar_para):
    try:
        config = DynamicEmailConfiguration.get_solo()
        email_sme = None
        emails_sme = Email.objects.filter(enviar_para=enviar_para, assunto=assunto, enviado=False)
        if not emails_sme:
            email_sme = Email.objects.create(enviar_para=enviar_para, assunto=assunto, body=mensagem)
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=config.from_email or None,
            recipient_list=[enviar_para]
        )
        if emails_sme.exists():
            emails_sme.update(enviado=True)
        elif email_sme:
            email_sme.enviado = True
            email_sme.save()
    except Exception as err:
        logger.error(str(err))


def enviar_email_html(assunto, template, contexto, enviar_para, html_salvo=None, lista_emails=None):
    try:

        config = DynamicEmailConfiguration.get_solo()
        msg_html = html_salvo or render_to_string(f"email/{template}.html", contexto)
        email_sme = None
        emails_sme = Email.objects.filter(enviar_para=enviar_para, assunto=assunto, enviado=False)
        if not emails_sme:
            email_sme = Email.objects.create(enviar_para=enviar_para, assunto=assunto, body=msg_html)
        emails = lista_emails or ListaEmail.objects.all()
        if emails:
            if lista_emails:
                email_utilizado = emails[contexto.get('id') % len(emails)]['email']
            else:
                email_utilizado = emails[contexto.get('id') % len(emails)].email
            config.from_email = email_utilizado
            config.username = email_utilizado
        msg = EmailMessage(
            subject=assunto, body=msg_html,
            from_email=config.from_email or None,
            bcc=(enviar_para,),
            connection=EmailBackend(**config.__dict__)
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        if emails_sme.exists():
            emails_sme.update(enviado=True)
        elif email_sme:
            email_sme.enviado = True
            email_sme.save()

    except Exception as err:
        logger.error(str(err))


def enviar_email_mp(assunto, mensagem, csv):
    try:
        config = DynamicEmailConfiguration.get_solo()
        email_mp = EmailMercadoPago.objects.first()
        email_novo = None
        email_ja_enviado = LogEmailMercadoPago.objects.filter(enviar_para=email_mp.email, assunto=assunto,
                                                              enviado=False, csv=csv)
        if not email_ja_enviado:
            email_novo = LogEmailMercadoPago.objects.create(enviar_para=email_mp.email, assunto=assunto,
                                                                  mensagem=mensagem, csv=csv)
        msg = EmailMessage(
            subject=assunto, body=mensagem,
            from_email=config.from_email or None,
            bcc=(email_mp.email,),
            connection=EmailBackend(**config.__dict__)
        )
        msg.send()
        if email_ja_enviado.exists():
            email_ja_enviado.update(enviado=True)
        elif email_novo:
            email_novo.enviado = True
            email_novo.save()
    except Exception as err:
        logger.error(str(err))
