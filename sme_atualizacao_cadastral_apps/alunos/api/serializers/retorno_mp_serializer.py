import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from sme_atualizacao_cadastral_apps.alunos.models import Responsavel, RetornoMP

log = logging.getLogger(__name__)


class RetornoMPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetornoMP
        fields = '__all__'


class RetornoMPCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        cpf = validated_data.get('cpf', False)
        codigo_eol = validated_data.get('codigo_eol', False)

        try:
            responsavel = Responsavel.objects.get(cpf=cpf, codigo_eol_aluno=codigo_eol)
            retorno = RetornoMP.objects.create(responsavel=responsavel, **validated_data)
            return retorno

        except Responsavel.DoesNotExist:
            raise ValidationError('Combinação CPF + Código EOL não encontrada na base.')

    class Meta:
        model = RetornoMP
        exclude = ('id', 'registro_processado')
