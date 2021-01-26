from requests import ConnectTimeout, ReadTimeout
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from ..serializers.aluno_serializer import (AlunoSerializer, AlunoLookUpSerializer, AlunoCreateSerializer,
                                            AlunoSerializerComCPFEol)
from ....eol_servico.utils import EOLService, EOLException
from ...models.aluno import Aluno
from ...models.responsavel import Responsavel


class AlunosViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'codigo_eol'
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

    def dados_dashboard(self, query_set: list, quantidade_desatualizados: int) -> dict:
        alunos_online = query_set.filter(responsavel__status__in=['ATUALIZADO_EOL', 'ATUALIZADO_VALIDO'],
                                         atualizado_na_escola=False,
                                         responsavel__pendencia_resolvida=False).count()
        alunos_escola = query_set.filter(responsavel__status__in=['ATUALIZADO_EOL', 'ATUALIZADO_VALIDO'],
                                         atualizado_na_escola=True,
                                         responsavel__pendencia_resolvida=False).count()
        desatualizados = quantidade_desatualizados
        pendencia_resolvida = query_set.filter(responsavel__pendencia_resolvida=True).count()
        divergente = query_set.filter(responsavel__status='DIVERGENTE').count()
        cpf_invalido = query_set.filter(responsavel__status='CPF_INVALIDO').count()
        email_invalido = query_set.filter(responsavel__status='EMAIL_INVALIDO').count()
        multiplos_emails = query_set.filter(responsavel__status='MULTIPLOS_EMAILS').count()
        inconsistencias_resolvidas = query_set.filter(responsavel__status='INCONSISTENCIA_RESOLVIDA').count()
        creditos_concedidos = query_set.filter(responsavel__status='CREDITO_CONCEDIDO').count()
        sumario = {
            'cadastros_validados': {
                'alunos_online': alunos_online,
                'alunos_escola': alunos_escola,
                'total': alunos_online + alunos_escola,
            },
            'cadastros_desatualizados': desatualizados,
            'cadastros_com_pendencias_resolvidas': pendencia_resolvida,
            'cadastros_divergentes': divergente,
            'total_alunos': query_set.count() + quantidade_desatualizados,
            'cpf_invalido': cpf_invalido,
            'email_invalido': email_invalido,
            'multiplos_emails': multiplos_emails,
            'inconsistencias_resolvidas': inconsistencias_resolvidas,
            'creditos_concedidos': creditos_concedidos,
        }

        return sumario

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        codigo_eol = self.request.query_params.get('codigo_eol', None)
        nome_estudante = self.request.query_params.get('nome_estudante', None)
        nome_responsavel = self.request.query_params.get('nome_responsavel', None)
        status_responsavel = self.request.query_params.get('status', None)

        if codigo_eol:
            queryset = queryset.filter(codigo_eol=codigo_eol)
            if not queryset and user.codigo_escola:
                EOLService.cria_aluno_desatualizado(codigo_eol=codigo_eol)

        if user.codigo_escola:
            queryset = queryset.filter(codigo_escola=user.codigo_escola)

        if nome_estudante:
            queryset = queryset.filter(nome=nome_estudante)

        if nome_responsavel:
            queryset = queryset.filter(responsavel__nome=nome_responsavel)

        if status_responsavel:
            status_reverse = dict((v, k) for k, v in Responsavel.STATUS_CHOICES)
            if status_responsavel == 'Cadastro Atualizado e validado':
                queryset = queryset.filter(
                    responsavel__status__in=['ATUALIZADO_EOL', 'ATUALIZADO_VALIDO'],
                    responsavel__pendencia_resolvida=False)
            elif status_responsavel == 'Cadastro com Pendência Resolvida':
                queryset = queryset.filter(responsavel__pendencia_resolvida=True)
            else:
                queryset = queryset.filter(responsavel__status=status_reverse[status_responsavel])

        return queryset.order_by('nome')

    def get_queryset_dashboard(self, codigo_escola=None):
        query_set = Aluno.objects.all()
        user = self.request.user
        if user.perfil_usuario == 'perfil_escola':
            query_set = query_set.filter(codigo_escola=user.codigo_escola)
        elif user.perfil_usuario == 'perfil_dre':
            query_set = query_set.filter(codigo_dre=user.codigo_dre)
            if codigo_escola:
                query_set = query_set.filter(codigo_escola=codigo_escola)
        return query_set

    def get_serializer_class(self):
        if self.action == 'list':
            return AlunoLookUpSerializer
        else:
            return AlunoCreateSerializer

    def list(self, request, *args, **kwargs):
        try:
            status_ = request.query_params.get('status')
            if not status_ or status_ != 'Cadastro Desatualizado':
                return Response(AlunoLookUpSerializer(self.get_queryset(), many=True).data)
            else:
                cod_eol_escola = request.user.codigo_escola
                response = EOLService.get_alunos_escola(cod_eol_escola)
                lista_codigo_eol = request.user.get_alunos_nao_desatualizados()
                alunos = [aluno for aluno in response if aluno['cd_aluno'] not in lista_codigo_eol]
                return Response(alunos)
        except EOLException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            return super(AlunosViewSet, self).create(request, *args, **kwargs)
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, codigo_eol=None, **kwargs):
        try:
            aluno = Aluno.objects.get(codigo_eol=codigo_eol)
            data = AlunoSerializerComCPFEol(aluno).data
            responsaveis = [data['responsaveis']]
            data['responsaveis'] = responsaveis
            return Response(data)
        except Aluno.DoesNotExist:
            return Response({'detail': 'Aluno não encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard(self, request):
        try:
            quantidade_desatualizados = 0
            if request.user.perfil_usuario == "perfil_escola":
                cod_eol_escola = request.user.codigo_escola
                response = EOLService.get_alunos_escola(cod_eol_escola)
                lista_codigo_eol = request.user.get_alunos_nao_desatualizados()
                alunos = [aluno for aluno in response if aluno['cd_aluno'] not in lista_codigo_eol]
                quantidade_desatualizados = len(alunos)
            codigo_eol_escola = request.query_params.get('cod_eol_escola', None)
            query_set = self.get_queryset_dashboard(codigo_eol_escola)
            response = {'results': self.dados_dashboard(
                query_set=query_set, quantidade_desatualizados=quantidade_desatualizados
            )}
            return Response(response, status=status.HTTP_200_OK)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
