import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authencticated_client):
    response = authencticated_client.get('/api/palavras-bloqueadas/')
    assert response.status_code == status.HTTP_200_OK
