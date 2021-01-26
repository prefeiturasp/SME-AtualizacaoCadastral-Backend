import pytest

from ..api.serializers.aluno_serializer import AlunoSerializer

pytestmark = pytest.mark.django_db


def test_aluno_serializer(aluno):
    aluno_serializer = AlunoSerializer(aluno)

    assert aluno_serializer.data is not None
    assert aluno_serializer.data['uuid']
    assert aluno_serializer.data['codigo_eol']
    assert aluno_serializer.data['data_nascimento']
    assert aluno_serializer.data['responsaveis']
    assert aluno_serializer.data['criado_em']
