import pytest
from ..models import BaseCadastro
from django.contrib import admin
from ..admin import BaseCadastroAdmin

pytestmark = pytest.mark.django_db


def test_instance_model(cadastro):
    model = cadastro
    assert isinstance(model, BaseCadastro)
    assert model.cpf
    assert model.situacao


def test_srt_model(cadastro):
    assert cadastro.__str__() == '55783647993 - 1 - Dirija-se a DRE'


def test_meta_modelo(cadastro):
    assert cadastro._meta.verbose_name == 'Base de cadastro'
    assert cadastro._meta.verbose_name_plural == 'Base de cadastros'


def test_admin():
    model_admin = BaseCadastroAdmin(BaseCadastro, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[BaseCadastro]
    assert model_admin.list_display == ('cpf', 'situacao',)
    assert model_admin.readonly_fields == ('cpf', 'situacao',)
