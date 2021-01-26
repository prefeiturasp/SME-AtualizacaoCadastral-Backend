from rest_framework import serializers

from sme_atualizacao_cadastral_apps.eol_servico.utils import EOLService
from .retorno_mp_serializer import RetornoMPSerializer
from ...models import Responsavel, validators, RetornoMP


class ResponsavelSerializer(serializers.ModelSerializer):
    nm_responsavel = serializers.CharField(source='nome')
    tp_pessoa_responsavel = serializers.CharField(source='vinculo')
    cd_cpf_responsavel = serializers.CharField(source='cpf', validators=[validators.cpf_validation])
    cd_ddd_celular_responsavel = serializers.CharField(source='ddd_celular', required=False, allow_null=True)
    nr_celular_responsavel = serializers.CharField(source='celular', validators=[validators.phone_validation],
                                                   required=False, allow_null=True)
    email_responsavel = serializers.CharField(source='email', validators=[validators.email_validation], required=False,
                                              allow_null=True)
    retornos = RetornoMPSerializer(many=True, required=False)
    aceita_divergencia = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Responsavel
        fields = ('codigo_eol_aluno', 'nm_responsavel', 'cd_cpf_responsavel', 'cd_ddd_celular_responsavel',
                  'nr_celular_responsavel', 'email_responsavel', 'tp_pessoa_responsavel', 'nome_mae',
                  'data_nascimento', 'status', 'nao_possui_celular', 'nao_possui_email', 'enviado_para_mercado_pago',
                  'retornos', 'aceita_divergencia')


class ResponsavelSerializerComCPFEOL(serializers.ModelSerializer):
    nm_responsavel = serializers.CharField(source='nome')
    tp_pessoa_responsavel = serializers.CharField(source='vinculo')
    cd_cpf_responsavel = serializers.CharField(source='cpf', validators=[validators.cpf_validation])
    cd_ddd_celular_responsavel = serializers.CharField(source='ddd_celular', required=False, allow_null=True)
    nr_celular_responsavel = serializers.CharField(source='celular', validators=[validators.phone_validation],
                                                   required=False, allow_null=True)
    email_responsavel = serializers.CharField(source='email', validators=[validators.email_validation], required=False,
                                              allow_null=True)
    cpf_eol = serializers.SerializerMethodField()
    nome_responsavel_eol = serializers.SerializerMethodField()
    retornos = serializers.SerializerMethodField()

    def get_cpf_eol(self, obj):
        return EOLService.get_cpf_eol_responsavel(obj.codigo_eol_aluno)

    def get_nome_responsavel_eol(self, obj):
        return EOLService.get_nome_eol_responsavel(obj.codigo_eol_aluno)

    def get_retornos(self, obj):
        if obj.status == 'MULTIPLOS_EMAILS':
            retornos = RetornoMPSerializer(obj.retornos.filter(ativo=True), many=True).data
            if retornos:
                emails = [retorno.responsavel.email for retorno in
                          RetornoMP.objects.filter(responsavel__cpf=obj.cpf, ativo=True).distinct(
                              'responsavel__email').all()]
                retornos[0]['emails'] = emails
            return retornos
        elif RetornoMP.objects.filter(cpf=obj.cpf).count() > 1:
            return RetornoMPSerializer(RetornoMP.objects.filter(cpf=obj.cpf, ativo=True).distinct('mensagem'),
                                       many=True).data
        else:
            return RetornoMPSerializer(obj.retornos.filter(ativo=True), many=True).data

    class Meta:
        model = Responsavel
        fields = ('codigo_eol_aluno', 'nm_responsavel', 'cd_cpf_responsavel', 'cd_ddd_celular_responsavel',
                  'nr_celular_responsavel', 'email_responsavel', 'tp_pessoa_responsavel', 'nome_mae',
                  'data_nascimento', 'status', 'cpf_eol', 'nao_possui_celular', 'nao_possui_email',
                  'enviado_para_mercado_pago', 'retornos', 'nome_responsavel_eol')


class ResponsavelListSerializer(serializers.ModelSerializer):
    codigo_eol = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    nome_aluno = serializers.SerializerMethodField()

    def get_codigo_eol(self, obj):
        return obj.alunos.codigo_eol

    def get_status(self, obj):
        return obj.get_status_display()

    def get_nome_aluno(self, obj):
        return obj.alunos.nome

    class Meta:
        model = Responsavel
        fields = ('nome', 'cpf', 'codigo_eol', 'status', 'nome_aluno')


class ResponsavelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        exclude = ('id', 'responsavel')
