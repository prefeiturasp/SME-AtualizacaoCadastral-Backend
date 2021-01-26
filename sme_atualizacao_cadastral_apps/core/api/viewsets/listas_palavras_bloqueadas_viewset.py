from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..serializers.lista_palavra_bloqueada_serializer import ListaPalavrasBloqueadasSerializer
from ...models.lista_palavras_bloqueadas import ListaPalavrasBloqueadas


class ListaPalavrasBloqueadasViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = ListaPalavrasBloqueadas.objects.all()
    serializer_class = ListaPalavrasBloqueadasSerializer

    def list(self, request, **kwargs):
        palavras = self.get_queryset().values_list('palavra', flat=True)
        return Response(palavras, status=status.HTTP_200_OK)
