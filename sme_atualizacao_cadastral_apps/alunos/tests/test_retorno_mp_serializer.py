import pytest

from ..api.serializers.retorno_mp_serializer import RetornoMPSerializer

pytestmark = pytest.mark.django_db


def test_aluno_serializer(retorno):
    retorno_serializer = RetornoMPSerializer(retorno)

    assert retorno_serializer.data is not None
    assert retorno_serializer.data['uuid']
    assert retorno_serializer.data['codigo_eol']
    assert retorno_serializer.data['data_ocorrencia']
    assert retorno_serializer.data['cpf']
    assert retorno_serializer.data['mensagem']
