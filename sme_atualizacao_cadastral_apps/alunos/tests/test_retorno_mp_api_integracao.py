import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_aluno_api_create_or_update(client_logado, payload_retorno_mp, monkeypatch):
    response = client_logado.post('/api/retorno-mp/', data=json.dumps(payload_retorno_mp), content_type='application'
                                                                                                        '/json')
    assert response.status_code == status.HTTP_201_CREATED
