from sme_atualizacao_cadastral_apps.cadastros.models import LogProcessamentoPlanilha


def salvar_log(arquivo, status, msg_retorno):
    log = LogProcessamentoPlanilha(
        arquivo=arquivo,
        status=status,
        msg_retorno=msg_retorno
    )
    log.save()
