import logging

import environ
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from .helpers import salvar_log
from .models import PlanilhaSituacao
from ..cadastros.services.import_xlsx import import_xlsx

env = environ.Env()
log = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    soft_time_limit=1200, time_limit=1200)
def processar_nova_base(planilha_id):
    try:
        planilha = PlanilhaSituacao.objects.get(id=planilha_id)
        log.info(f'Inicia processo de extração e importação dos dados da planilha:')
        import_xlsx(planilha)
    except ObjectDoesNotExist:
        salvar_log(arquivo=f'planilha id {planilha_id}', status=False, msg_retorno='Planilha não existe na base')
