import pytest

from ..models import RetornoMP

pytestmark = pytest.mark.django_db


def test_instance_model(retorno):
    model = retorno
    assert isinstance(model, RetornoMP)
    assert model.codigo_eol
    assert model.cpf
    assert model.status
    assert model.mensagem
    assert model.data_ocorrencia


def test_srt_model(retorno):
    assert retorno.__str__() == '00000000000 - 3872240'


def test_meta_modelo(retorno):
    assert retorno._meta.verbose_name == 'Retorno do Mercado Pago'
    assert retorno._meta.verbose_name_plural == 'Retornos do Mercado Pago'
