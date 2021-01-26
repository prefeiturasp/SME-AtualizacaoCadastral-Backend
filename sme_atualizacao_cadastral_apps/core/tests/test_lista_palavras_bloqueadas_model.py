import pytest
from model_bakery import baker
from ..models import ListaPalavrasBloqueadas
from django.contrib import admin
from ..admin import ListaPalavrasBloqueadasAdmin

pytestmark = pytest.mark.django_db


def test_instance_model():
    palavra = 'teste'
    model = baker.make('ListaPalavrasBloqueadas', palavra=palavra)
    assert isinstance(model, ListaPalavrasBloqueadas)


def test_srt_model():
    palavra = 'teste'
    model = baker.make('ListaPalavrasBloqueadas', palavra=palavra)
    assert model.__str__() == palavra


def test_meta_modelo():
    model = baker.make('ListaPalavrasBloqueadas')
    assert model._meta.verbose_name == 'Lista palavra bloqueada'
    assert model._meta.verbose_name_plural == 'Lista palavras bloqueadas'


def test_admin():
    model_admin = ListaPalavrasBloqueadasAdmin(ListaPalavrasBloqueadas, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[ListaPalavrasBloqueadas]
    assert model_admin.list_display == ('palavra', 'criado_em',)
    assert model_admin.search_fields == ('palavra',)
