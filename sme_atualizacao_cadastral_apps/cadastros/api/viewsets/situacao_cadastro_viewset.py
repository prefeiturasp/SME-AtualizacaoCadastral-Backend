from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..serializers.situacao_cadastro_serializer import BaseCadastroSerializer, PlanilhaSituacaoSerializer
from ...models.situacao_cadastro import BaseCadastro, PlanilhaSituacao


class BaseCadastroViewSet(mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'cpf'
    queryset = BaseCadastro.objects.all()
    serializer_class = BaseCadastroSerializer


class PlanilhaSituacaoViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = PlanilhaSituacao.objects.all()
    serializer_class = PlanilhaSituacaoSerializer

    def list(self, request, **kwargs):
        datas = self.get_queryset().filter(extraido=True).last()
        return Response(PlanilhaSituacaoSerializer(datas, many=False).data)
