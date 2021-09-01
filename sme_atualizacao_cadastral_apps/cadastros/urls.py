from django.urls import path, include
from rest_framework import routers

from .api.viewsets.situacao_cadastro_viewset import BaseCadastroViewSet, PlanilhaSituacaoViewSet

router = routers.DefaultRouter()

router.register('base-cadastros', BaseCadastroViewSet)
router.register('datas-corte', PlanilhaSituacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
