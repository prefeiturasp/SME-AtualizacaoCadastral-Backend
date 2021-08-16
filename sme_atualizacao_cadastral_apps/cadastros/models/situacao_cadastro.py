from django.db import models


class PlanilhaSituacao(models.Model):
    arquivo = models.FileField(
        'Planilha', upload_to='situacao_cadastro/planilhas',
        help_text='Arquivo no formato <strong>.xlsx</strong> com duas colunas, sendo os seguintes titulos:'
                  '<strong>CD_CPF_RESPONSAVEL e MSG</strong> | A primeira coluna deve conter apenas os números do CPF '
                  'e a segunda coluna apenas o número da situação'
    )
    data_corte_planilha = models.DateField('Data de corte da planilha')
    data_corte_lote = models.DateField('Data de corte do lote')
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)
    extraido = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = 'Planilha de Situação Cadastral'
        verbose_name_plural = 'Planilhas de Situações Cadastrais'

    def __str__(self):
        return f'{self.arquivo.name.split("/")[-1]}'

    def processar_planilha(self):
        from sme_atualizacao_cadastral_apps.cadastros.tasks import processar_nova_base
        from sme_atualizacao_cadastral_apps.cadastros.helpers import salvar_log

        if not self.extraido:
            processar_nova_base.delay(planilha_id=self.id)
        else:
            salvar_log(
                arquivo=str(self.arquivo.name.split("/")[-1]),
                status=False,
                msg_retorno='Esse registro já foi processdo anteriormente.'
            )


class BaseCadastro(models.Model):
    # Situacao Choice
    SITUACAO_DRE = 1
    SITUACAO_UNIDADE_ESCOLAR = 2
    SITUACAO_CADASTRO_OK = 3

    SITUACAO_NOMES = {
        SITUACAO_DRE: '1 - Dirija-se a DRE',
        SITUACAO_UNIDADE_ESCOLAR: '2 - Dirija-se a unidade escolar',
        SITUACAO_CADASTRO_OK: '3 - Cadastro completo',
    }

    SITUACAO_CHOICES = (
        (SITUACAO_DRE, SITUACAO_NOMES[SITUACAO_DRE]),
        (SITUACAO_UNIDADE_ESCOLAR, SITUACAO_NOMES[SITUACAO_UNIDADE_ESCOLAR]),
        (SITUACAO_CADASTRO_OK, SITUACAO_NOMES[SITUACAO_CADASTRO_OK]),
    )

    cpf = models.CharField("CPF", max_length=11)
    situacao = models.IntegerField(
        'Situação',
        choices=SITUACAO_CHOICES,
        default=SITUACAO_UNIDADE_ESCOLAR
    )

    class Meta:
        verbose_name = 'Base de cadastro'
        verbose_name_plural = 'Base de cadastros'

    def __str__(self):
        return f'{self.cpf} - {self.get_situacao_display()}'


class LogProcessamentoPlanilha(models.Model):
    arquivo = models.CharField('Nome do arquivo', null=True, max_length=255)
    criado_em = models.DateTimeField("Criado em", editable=False, auto_now_add=True)
    status = models.BooleanField('Status', default=False, editable=False)
    msg_retorno = models.TextField('Mensagem')

    class Meta:
        verbose_name = 'Log de processamento'
        verbose_name_plural = 'Logs de processamento'

    def __str__(self):
        status = 'ok' if self.status else 'falha'
        return f'{self.arquivo} - {status}'
