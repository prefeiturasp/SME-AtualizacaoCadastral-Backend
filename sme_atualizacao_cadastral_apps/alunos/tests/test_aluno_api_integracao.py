import json

import pytest
from rest_framework import status
from .conftest import mocked_request_api_eol
from ..api.serializers.aluno_serializer import AlunoCreateSerializer
from ..models import Responsavel

pytestmark = pytest.mark.django_db


def test_aluno_api_retrieve(client_logado, aluno):
    response = client_logado.get(f'/api/alunos/{aluno.codigo_eol}/')
    assert response.status_code == status.HTTP_200_OK
    assert str(aluno.codigo_eol) in response.content.decode("utf-8")


def test_aluno_api_create_or_update(client_logado, payload, monkeypatch):
    monkeypatch.setattr(AlunoCreateSerializer, 'atualiza_payload',
                        lambda p1, p2: mocked_request_api_eol())
    response = client_logado.post('/api/alunos/', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED


def test_aluno_api_create_or_update_responsavel_com_erro(client_logado_responsavel_erro,
                                                         payload_responsavel_erro,
                                                         monkeypatch):
    monkeypatch.setattr(AlunoCreateSerializer, 'atualiza_payload',
                        lambda p1, p2: mocked_request_api_eol())
    response = client_logado_responsavel_erro.post(
        '/api/alunos/',
        data=json.dumps(payload_responsavel_erro),
        content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    responsavel = response.json().get('responsavel')
    assert responsavel.get('status') == 'INCONSISTENCIA_RESOLVIDA'
    assert responsavel.get('retornos')[0].get('ativo') is False
    assert responsavel.get('enviado_para_mercado_pago') is False


def test_aluno_api_create_or_update_dois_responsaveis_com_erro(client_logado_responsavel_erro,
                                                               payload_responsavel_erro,
                                                               monkeypatch):
    monkeypatch.setattr(AlunoCreateSerializer, 'atualiza_payload',
                        lambda p1, p2: mocked_request_api_eol())
    response = client_logado_responsavel_erro.get(
        '/api/responsaveis/',
        content_type='application/json')
    # Somente um responsável, pois não retorna responsáveis com o mesmo CPF
    assert len(response.json()) == 1
    assert response.status_code == status.HTTP_200_OK
    response = client_logado_responsavel_erro.post(
        '/api/alunos/',
        data=json.dumps(payload_responsavel_erro),
        content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    response = client_logado_responsavel_erro.get(
        '/api/responsaveis/',
        content_type='application/json')
    # Uma vez com a inconsistência resolvida de ambos, não retorna mais responsaveis
    assert len(response.json()) == 0
    # Checa se todos os responsáveis com o mesmo CPF foram alterados
    for responsavel in Responsavel.objects.all():
        assert responsavel.status == 'INCONSISTENCIA_RESOLVIDA'
        assert responsavel.email == 'emailcorrigido@emailcorrigido.com'
        assert responsavel.enviado_para_mercado_pago is False
        assert responsavel.retornos.filter(ativo=True).count() is 0


def test_aluno_api_create_or_update_multiplos_emails(client_logado_multiplos_emails,
                                                     payload_responsavel_erro,
                                                     monkeypatch):
    monkeypatch.setattr(AlunoCreateSerializer, 'atualiza_payload',
                        lambda p1, p2: mocked_request_api_eol())
    response = client_logado_multiplos_emails.get(
        '/api/responsaveis/',
        content_type='application/json')
    # Somente um responsável, pois não retorna responsáveis com o mesmo CPF
    assert len(response.json()) == 1
    assert response.status_code == status.HTTP_200_OK
    response = client_logado_multiplos_emails.get(
        '/api/alunos/3872240/',
        content_type='application/json')
    # Somente um responsável, pois não retorna responsáveis com o mesmo CPF
    assert response.status_code == status.HTTP_200_OK
    responsavel = response.json().get('responsaveis')[0]
    emails = responsavel.get('retornos')[0].get('emails')
    assert emails == ['email1@teste.com', 'email2@teste.com']
    response = client_logado_multiplos_emails.post(
        '/api/alunos/',
        data=json.dumps(payload_responsavel_erro),
        content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    response = client_logado_multiplos_emails.get(
        '/api/responsaveis/',
        content_type='application/json')
    # Uma vez com a inconsistência resolvida de ambos, não retorna mais responsaveis
    assert len(response.json()) == 0
    # Checa se todos os responsáveis com o mesmo CPF foram alterados
    for responsavel in Responsavel.objects.all():
        assert responsavel.status == 'INCONSISTENCIA_RESOLVIDA'
        assert responsavel.email == 'emailcorrigido@emailcorrigido.com'
        assert responsavel.enviado_para_mercado_pago is False
        assert responsavel.retornos.filter(ativo=True).count() is 0


def test_dashboard(client_logado):
    response = client_logado.get(f'/api/alunos/dashboard/')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results')
    assert 'cadastros_com_pendencias_resolvidas' in results
    assert 'cadastros_validados' in results
    assert 'alunos_online' in results['cadastros_validados']
    assert 'alunos_escola' in results['cadastros_validados']
    assert 'total' in results['cadastros_validados']
    assert 'cadastros_desatualizados' in results
    assert 'cadastros_com_pendencias_resolvidas' in results
    assert 'cadastros_divergentes' in results
    assert 'total_alunos' in results
    assert 'cpf_invalido' in results
    assert 'email_invalido' in results
    assert 'multiplos_emails' in results
    assert 'inconsistencias_resolvidas' in results
    assert 'creditos_concedidos' in results


def test_dashboard_com_dados(client_logado_multiplos_emails, responsaveis_dashboard):
    response = client_logado_multiplos_emails.get(f'/api/alunos/dashboard/')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results')
    assert results['multiplos_emails'] == 2
    assert results['email_invalido'] == 1
    assert results['cpf_invalido'] == 1
    assert results['cadastros_validados']['alunos_online'] == 1
    assert results['cadastros_validados']['alunos_escola'] == 1
    assert results['cadastros_validados']['total'] == 2
