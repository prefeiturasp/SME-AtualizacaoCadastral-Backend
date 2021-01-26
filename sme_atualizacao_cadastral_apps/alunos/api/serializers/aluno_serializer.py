import logging

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import serializers, status

from .responsavel_serializer import ResponsavelSerializerComCPFEOL
from ...models import Aluno, Responsavel
from ...api.serializers.responsavel_serializer import ResponsavelSerializer
from sme_atualizacao_cadastral_apps.eol_servico.utils import EOLService, EOLException

log = logging.getLogger(__name__)


class AlunoSerializer(serializers.ModelSerializer):
    responsaveis = ResponsavelSerializer(source='responsavel')
    codigo_eol = serializers.CharField(read_only=True)

    class Meta:
        model = Aluno
        fields = ('uuid', 'codigo_eol', 'nome', 'data_nascimento', 'codigo_escola', 'codigo_dre',
                  'criado_em', 'responsaveis')


class AlunoSerializerComCPFEol(serializers.ModelSerializer):
    responsaveis = ResponsavelSerializerComCPFEOL(source='responsavel')
    codigo_eol = serializers.CharField(read_only=True)

    class Meta:
        model = Aluno
        fields = ('uuid', 'codigo_eol', 'nome', 'data_nascimento', 'codigo_escola', 'codigo_dre',
                  'criado_em', 'responsaveis')


class AlunoLookUpSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('get_status')
    responsavel_nome = serializers.SerializerMethodField()

    def get_responsavel_nome(self, obj):
        return obj.responsavel.nome

    def get_status(self, obj):
        return obj.responsavel.get_status_display()

    class Meta:
        model = Aluno
        fields = ('codigo_eol', 'nome', 'data_nascimento', 'status', 'responsavel_nome')


class AlunoCreateSerializer(serializers.ModelSerializer):
    codigo_eol = serializers.CharField()
    responsavel = ResponsavelSerializer()
    inconsistencia_resolvida = serializers.BooleanField(required=False)

    def get_status(self, codigo_eol, cpf, atualizado_na_escola, nome=None):
        if ((EOLService.cpf_divergente(codigo_eol, cpf) or (nome and EOLService.nome_divergente(codigo_eol, nome)))
            and atualizado_na_escola):  # noqa
            return 'PENDENCIA_RESOLVIDA'
        elif EOLService.cpf_divergente(codigo_eol, cpf):
            return 'DIVERGENTE'
        elif atualizado_na_escola:
            return 'ATUALIZADO_VALIDO'
        else:
            return 'ATUALIZADO_VALIDO'

    def atualiza_payload(self, validated_data):
        try:
            informacoes_aluno = EOLService.get_informacoes_responsavel(validated_data['codigo_eol'])
            validated_data['nome'] = informacoes_aluno.get('nome') or informacoes_aluno.get('nm_aluno')
            validated_data['codigo_escola'] = informacoes_aluno.get('codigo_escola') or informacoes_aluno.get(
                'cd_escola')
            validated_data['codigo_dre'] = informacoes_aluno.get('codigo_dre') or informacoes_aluno.get('cd_dre')
            return validated_data
        except EOLException as e:
            log.info(f"Erro ao buscar informações do aluno: {e}")
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, validated_data):
        '''
        Código responsavel por criar e atualizar as informações de responsaveis e alunos.
        Este código atende ao pedido de uniforme portal da familia, painel admin escola e painel inconsistência escola.
        Quando existe inconsistência resolvida significa que todos os responsaveis com o mesmo cpf são atualizados com
        os mesmos dados.
        '''
        atualizado_na_escola = validated_data.get('atualizado_na_escola', False)
        inconsistencia_resolvida = validated_data.pop('inconsistencia_resolvida', False)
        user = self.context['request'].user
        responsavel = validated_data.pop('responsavel')
        if inconsistencia_resolvida:
            codigo_eol_aluno = responsavel.pop('codigo_eol_aluno')
            cpf = Aluno.objects.get(codigo_eol=codigo_eol_aluno).responsavel.cpf
            lista_eol_alunos = Responsavel.objects.filter(cpf=cpf).exclude(
                status=Responsavel.STATUS_CREDITO_CONCEDIDO).values_list('codigo_eol_aluno', flat=True)
            aluno = Aluno.objects.get(codigo_eol=validated_data['codigo_eol'])
            log.info(f"Inicia atualizações dos responsaveis com cpf {cpf}")
            for codigo_eol in lista_eol_alunos:
                responsavel['status'] = Responsavel.STATUS_INCONSISTENCIA_RESOLVIDA
                responsavel['enviado_para_mercado_pago'] = False
                responsavel['responsavel_alterado'] = True
                responsavel_criado, created = Responsavel.objects.update_or_create(
                    codigo_eol_aluno=codigo_eol,
                    defaults={**responsavel}
                )
                log.info(f"Responsavel Atualizado. Eol aluno: {codigo_eol}, "
                         f"nome responsavel: {responsavel_criado.nome}")
                responsavel_criado.salvar_no_eol()
                log.info(f"Atualizando retorno do responsavel {responsavel_criado.nome} para ativo false.")
                responsavel_criado.retornos.filter(ativo=True).update(ativo=False)
            return aluno
        else:
            cpf = responsavel.get('cpf', None)
            nome = responsavel.get('nome', None)
            aceita_divergencia = responsavel.pop('aceita_divergencia', False)
            cpf_divergente = EOLService.cpf_divergente(validated_data['codigo_eol'], cpf)
            nome_divergente = EOLService.nome_divergente(validated_data['codigo_eol'], nome)
            if atualizado_na_escola:
                validated_data['servidor'] = user.username
            log.info(f"Criando Aluno com códio eol: {validated_data.get('codigo_eol')}")
            self.atualiza_payload(validated_data)
            try:
                aluno_obj = Aluno.objects.get(codigo_eol=validated_data['codigo_eol'])
                if aluno_obj.responsavel.enviado_para_mercado_pago and not user.codigo_escola:
                    raise ValidationError('Solicitação enviada para o mercado pago.')
                elif aluno_obj.responsavel.status == 'INCONSISTENCIA_RESOLVIDA' and not user.codigo_escola:
                    raise ValidationError('Solicitação com inconsistência resolvida. Não pode atualizar os dados.')
                elif ((aluno_obj.atualizado_na_escola or aluno_obj.responsavel.status == 'ATUALIZADO_EOL')
                      and not user.codigo_escola):  # noqa
                    raise ValidationError('Solicitação finalizada. Não pode atualizar os dados.')
                else:
                    if not aceita_divergencia and not cpf_divergente and nome_divergente and not user.codigo_escola:
                        raise AssertionError('Solicitação com inconsistência no nome.')

                if aceita_divergencia and not user.codigo_escola:
                    responsavel['status'] = 'DIVERGENTE'
                else:
                    responsavel['status'] = self.get_status(validated_data['codigo_eol'], cpf, atualizado_na_escola, nome)
                if responsavel['status'] == 'PENDENCIA_RESOLVIDA':
                    responsavel['pendencia_resolvida'] = True
                responsavel_criado, created = Responsavel.objects.update_or_create(
                    codigo_eol_aluno=validated_data['codigo_eol'], defaults={**responsavel})
                log.info(
                    f"Aluno existe. Eol: {validated_data['codigo_eol']}, nome responsavel: {responsavel_criado.nome}")
            except Aluno.DoesNotExist:
                if not aceita_divergencia and not cpf_divergente and nome_divergente and not user.codigo_escola:
                    raise AssertionError('Solicitação com inconsistência no nome.')
                elif aceita_divergencia and not user.codigo_escola:
                    responsavel['status'] = 'DIVERGENTE'
                else:
                    responsavel['status'] = self.get_status(validated_data['codigo_eol'], cpf, atualizado_na_escola, nome)
                if responsavel['status'] == 'PENDENCIA_RESOLVIDA':
                    responsavel['pendencia_resolvida'] = True
                responsavel_criado, created = Responsavel.objects.update_or_create(**responsavel)
                validated_data['responsavel'] = responsavel_criado
                log.info(
                    f"Aluno criado. Eol: {validated_data['codigo_eol']}, nome responsavel: {responsavel_criado.nome}")
            codigo = validated_data.pop('codigo_eol')
            aluno, created = Aluno.objects.update_or_create(codigo_eol=codigo, defaults={**validated_data})
            log.info("Inicia envio de email.")
            responsavel_criado.enviar_email()
            if responsavel_criado.status == 'ATUALIZADO_VALIDO' or responsavel_criado.status == 'PENDENCIA_RESOLVIDA':
                responsavel_criado.salvar_no_eol()
            log.info("Aluno Criado/Atualizado.")
            return aluno

    class Meta:
        model = Aluno
        exclude = ('id',)
