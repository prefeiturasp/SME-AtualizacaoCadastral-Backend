from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..serializers.responsavel_serializer import ResponsavelListSerializer
from ...models.responsavel import Responsavel


class ResponsaveisViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'cpf'
    queryset = Responsavel.objects.all()
    serializer_class = ResponsavelListSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        codigo_eol = self.request.query_params.get('codigo_eol', None)
        nome_estudante = self.request.query_params.get('nome_estudante', None)
        nome_responsavel = self.request.query_params.get('nome_responsavel', None)
        cpf_responsavel = self.request.query_params.get('cpf_responsavel', None)
        status_responsavel = self.request.query_params.get('status', None)

        queryset = queryset.filter(
            status__in=['CPF_INVALIDO', 'EMAIL_INVALIDO', 'MULTIPLOS_EMAILS']
        )

        if codigo_eol:
            queryset = queryset.filter(alunos__codigo_eol=codigo_eol)

        if user.codigo_escola:
            queryset = queryset.filter(alunos__codigo_escola=user.codigo_escola)

        if nome_estudante:
            queryset = queryset.filter(alunos__nome=nome_estudante)

        if cpf_responsavel:
            queryset = queryset.filter(cpf=cpf_responsavel)

        if nome_responsavel:
            queryset = queryset.filter(nome=nome_responsavel)

        if status_responsavel:
            status_reverse = dict((v, k) for k, v in Responsavel.STATUS_CHOICES)
            queryset = queryset.filter(status=status_reverse[status_responsavel])

        return queryset.distinct('cpf')
