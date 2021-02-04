import pytest
from django.contrib import admin
from ..models import Responsavel
from ..admin import ResponsavelAdmin

pytestmark = pytest.mark.django_db


def test_instance_model(responsavel):
    model = responsavel
    assert isinstance(model, Responsavel)
    assert model.codigo_eol_aluno
    assert model.nome
    assert model.vinculo
    assert model.cpf
    assert model.email
    assert model.ddd_celular
    assert model.celular
    assert model.data_nascimento
    assert model.nome_mae
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status


def test_srt_model(responsavel):
    assert responsavel.__str__() == 'Fulano - Cod. EOL Aluno: 3872240'


def test_meta_modelo(responsavel):
    assert responsavel._meta.verbose_name == 'Responsavel'
    assert responsavel._meta.verbose_name_plural == 'Responsaveis'


def test_admin():
    model_admin = ResponsavelAdmin(Responsavel, admin.site)
    assert admin.site._registry[Responsavel]
    assert model_admin.list_display == (
        'nome', 'cpf', 'codigo_eol_aluno', 'data_nascimento', 'vinculo', 'nome_mae', 'get_celular', 'email',
        'status', 'criado_em')
    assert model_admin.ordering == ('-alterado_em',)
    assert model_admin.search_fields == ('uuid', 'cpf', 'nome', 'codigo_eol_aluno')


def test_responsavel_status_default_atualizado(responsavel):
    assert responsavel.status == Responsavel.STATUS_ATUALIZADO_VALIDO
