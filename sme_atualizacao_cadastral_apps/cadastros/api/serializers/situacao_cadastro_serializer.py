from rest_framework import serializers

from ...models import BaseCadastro, PlanilhaSituacao


class BaseCadastroSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseCadastro
        fields = ('cpf', 'situacao')


class PlanilhaSituacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanilhaSituacao
        fields = ('data_corte_planilha', 'data_corte_lote')
