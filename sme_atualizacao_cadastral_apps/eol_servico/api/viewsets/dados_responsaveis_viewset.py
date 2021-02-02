from requests import ConnectTimeout, ReadTimeout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ...utils import EOLException, EOLService, aluno_existe
import datetime


class DadosResponsavelEOLViewSet(ViewSet):
    lookup_field = 'codigo_eol'
    permission_classes = (IsAuthenticated,)
    many = False

    @action(detail=False, methods=['post'])
    def busca_dados(self, request):
        try:
            codigo_eol = request.data["codigo_eol"]
            dados = EOLService.get_informacoes_responsavel(codigo_eol)
            data_nascimento_request = datetime.datetime.strptime(request.data["data_nascimento"], "%Y-%m-%d")
            if aluno_existe(codigo_eol):
                data_nascimento_banco = datetime.datetime.strptime(dados['data_nascimento'], "%Y-%m-%d")
                if data_nascimento_request.date() == data_nascimento_banco.date():
                    return Response({'detail': dados})
                else:
                    return Response({'detail': 'Data de nascimento invalida para o código eol informado'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                dados_responsavel = dados['responsaveis'][0]
                if not EOLService.tem_informacao_faltando(dados_responsavel):
                    raise EOLException('Os dados do responsável já estão completos no EOL.')

                data_nascimento_eol = datetime.datetime.strptime(dados['dt_nascimento_aluno'], "%Y-%m-%dT%H:%M:%S")
                if data_nascimento_request.date() == data_nascimento_eol.date():
                    if dados['recadastra'] == 'S':
                        EOLService.registra_log(codigo_eol=codigo_eol, json=dados)
                        if dados['responsaveis']:
                            if not request.user.codigo_escola:
                                dados['responsaveis'][0].pop('cd_cpf_responsavel')
                        return Response({'detail': dados})
                    else:
                        return Response({'detail': 'Este estudante não faz parte do público do programa de uniforme '
                                                   'escolar'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Data de nascimento invalida para o código eol informado'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
