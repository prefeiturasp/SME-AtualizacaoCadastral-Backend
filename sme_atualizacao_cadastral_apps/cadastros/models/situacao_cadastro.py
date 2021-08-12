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
        from sme_atualizacao_cadastral_apps.cadastros.services.import_xlsx import import_xlsx
        import_xlsx(self)


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
