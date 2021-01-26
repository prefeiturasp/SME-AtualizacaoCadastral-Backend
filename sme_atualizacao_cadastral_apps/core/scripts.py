import datetime

from sme_atualizacao_cadastral_apps.alunos.models import Responsavel
from sme_atualizacao_cadastral_apps.alunos.tasks import enviar_email_simples
from sme_atualizacao_cadastral_apps.users.models import User


def enviar_email_campo_confuso():
    data = datetime.datetime(2020, 3, 9, 17, 0)
    responsaveis = Responsavel.objects.filter(criado_em__lt=data)
    emails = [responsavel['email'] for responsavel in list(responsaveis.values('email')) if responsavel['email']]
    conteudo = ('Caro(a) cidadão(ã),\n\nAo fazer a solicitação do uniforme escolar, no campo “Nome da mãe do ' +
                'responsável (sem abreviações)”, a informação da qual precisamos é o nome da sua mãe (a mãe do ' +
                'responsável – ou seja, na maioria dos casos, da avó da criança).\n\nPor favor, caso tenha se ' +
                'enganado e digitado, por exemplo, o nome da mãe da criança, entre novamente no ' +
                'https://pedido-uniforme.sme.prefeitura.sp.gov.br/. Aí, é só seguir os mesmos passos de quando ' +
                'fez a solicitação: informar o Código EOL e data de nascimento da criança. Depois, corrigir o nome ' +
                'da mãe do responsável (sua mãe) no campo “Nome da mãe do responsável (sem abreviações)”. Depois, ' +
                'é só clicar em “Solicitar uniforme”.\n\nObrigada!\n\nAtenciosamente,\n\n' +
                'Secretaria Municipal de Educação\nPrefeitura de São Paulo')
    assunto = 'Uniforme escolar - verifique os dados do nome da mãe do responsável pela criança'
    for email in emails:
        enviar_email_simples.delay(
            assunto=assunto,
            mensagem=conteudo,
            enviar_para=email
        )


def enviar_email_usuarios_inativos():
    usuarios = User.objects.filter(is_active=False)
    for usuario in usuarios:
        usuario.enviar_email_confirmacao()
