from rest_framework import routers
from django.urls import include, path

from .api.viewsets.dados_responsaveis_viewset import DadosResponsavelEOLViewSet

router = routers.DefaultRouter()

router.register('dados-responsavel', DadosResponsavelEOLViewSet, basename='Dados Responsavel EOL')

urlpatterns = [
    path('', include(router.urls)),
]
