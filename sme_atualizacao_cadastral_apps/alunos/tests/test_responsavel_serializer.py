import pytest

from ..api.serializers.responsavel_serializer import ResponsavelSerializer

pytestmark = pytest.mark.django_db


def test_responsavel_serializer(responsavel):
    responsavel_serializer = ResponsavelSerializer(responsavel)

    assert responsavel_serializer.data is not None
    assert responsavel_serializer.data['cd_cpf_responsavel']
    assert responsavel_serializer.data['nm_responsavel']
    assert responsavel_serializer.data['data_nascimento']
    assert responsavel_serializer.data['cd_ddd_celular_responsavel']
    assert responsavel_serializer.data['nr_celular_responsavel']
    assert responsavel_serializer.data['nome_mae']
    assert responsavel_serializer.data['tp_pessoa_responsavel']
    assert responsavel_serializer.data['email_responsavel']

