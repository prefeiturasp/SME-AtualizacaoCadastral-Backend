import logging

from ..tasks import enviar_email_solicitacao_uniforme
from ..models.responsavel import Responsavel

log = logging.getLogger(__name__)


class ProcessarRetornoService(object):

    @classmethod
    def enviar_email_inconsistencia(self, responsavel):
        enviar_email_solicitacao_uniforme.delay(
            'Inconsistência nos dados informados', 'email_inconsistencia', responsavel.email,
            {'nome': responsavel.alunos.nome, 'id': responsavel.id})

    @classmethod
    def processar_todos_credito_consedido(cls):
        from ..models.retorno_mp import RetornoMP
        try:
            retornos = RetornoMP.objects.filter(
                registro_processado=False, status=RetornoMP.STATUS_CREDITADO).values_list('codigo_eol', flat=True)
            Responsavel.objects.filter(codigo_eol_aluno__in=retornos).update(
                status=Responsavel.STATUS_CREDITO_CONCEDIDO)
            retornos.update(registro_processado=True)
        except Exception as e:
            log.error('Falha no processamento: ' + str(e))

    @classmethod
    def cpf_invalido(cls, responsavel_id):
        log.info(f"Inicia processo de atualização para cpf invalido")
        try:
            responsavel = Responsavel.objects.get(id=responsavel_id)
            responsavel.status = Responsavel.STATUS_CPF_INVALIDO
            responsavel.save()
            log.info(f"responsavel pelo aluno {responsavel.codigo_eol_aluno} atualizado para cpf invalido")
            log.info(f'Enviando email inconsistencia para: {responsavel.email}.')
            log.info(f"Inicia envio de e-mail de inconsistencia")
            if responsavel.email:
                cls.enviar_email_inconsistencia(responsavel)

        except Responsavel.DoesNotExist:
            log.info(f"Resposavel informado não existe na base")

    @classmethod
    def multiplos_emails(cls, responsavel_id):
        log.info(f"Inicia processo de atualização para multiplos e-mails")
        try:
            responsavel = Responsavel.objects.get(id=responsavel_id)
            responsavel.status = Responsavel.STATUS_MULTIPLOS_EMAILS
            responsavel.save()
            log.info(f"responsavel pelo aluno {responsavel.codigo_eol_aluno} atualizado para multiplos e-mails")
            log.info(f"Inicia envio de e-mail de inconsistencia")
            if responsavel.email:
                cls.enviar_email_inconsistencia(responsavel)

        except Responsavel.DoesNotExist:
            log.info(f"Resposavel informado não existe na base")
