import pytest
from model_bakery import baker


@pytest.fixture
def cadastro():
    return baker.make(
        'BaseCadastro',
        cpf='55783647993',
        situacao=1
    )
