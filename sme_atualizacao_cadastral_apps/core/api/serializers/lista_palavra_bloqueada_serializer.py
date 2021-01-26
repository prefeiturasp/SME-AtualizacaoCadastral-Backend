from rest_framework import serializers

from ...models import ListaPalavrasBloqueadas


class ListaPalavrasBloqueadasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaPalavrasBloqueadas
        fields = ('palavra',)
