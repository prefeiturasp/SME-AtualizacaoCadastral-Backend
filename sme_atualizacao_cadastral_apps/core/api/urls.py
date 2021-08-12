from rest_framework import routers
from django.urls import include, path
from .viewsets.version_viewset import ApiVersion
from .viewsets.listas_palavras_bloqueadas_viewset import ListaPalavrasBloqueadasViewSet
from ...eol_servico.urls import router as servico_eol_router
from ...alunos.urls import router as aluno_router
from ...cadastros.urls import router as base_cadastro_router
from ...users.urls import router as users_router

# Importe aqui as rotas das demais aplicações

router = routers.DefaultRouter()

router.register('versao', ApiVersion, basename='Version'),
router.register('palavras-bloqueadas', ListaPalavrasBloqueadasViewSet, basename='ListaPalavrasBloqueadasViewSet')

# Adicione aqui as rotas das demais aplicações para que as urls sejam exibidas na API Root do DRF
router.registry.extend(servico_eol_router.registry)
router.registry.extend(aluno_router.registry)
router.registry.extend(base_cadastro_router.registry)
router.registry.extend(users_router.registry)

urlpatterns = [
    path('', include(router.urls))
]
