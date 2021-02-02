import logging
import datetime

import environ
import requests
from rest_framework import status
from requests.auth import HTTPBasicAuth

from ..alunos.models import Aluno, Responsavel, LogErroAtualizacaoEOL
from ..alunos.models.log_consulta_eol import LogConsultaEOL
from ..alunos.api.services.aluno_service import AlunoService
from .helpers import ajusta_cpf
from ..core.constants import ESCOLAS_CEI
from ..core.utils import remove_accents

env = environ.Env()
DJANGO_EOL_API_TOKEN = env('DJANGO_EOL_API_TOKEN')
DJANGO_EOL_API_URL = env('DJANGO_EOL_API_URL')
DJANGO_EOL_API_ATUALIZAR_URL = env('DJANGO_EOL_API_ATUALIZAR_URL')
USUARIO_EOL_API = env('DJANGO_EOL_API_USER')
SENHA_EOL_API = env('DJANGO_EOL_API_PASSWORD')
DJANGO_EOL_API_TERC_TOKEN = env('DJANGO_EOL_API_TERC_TOKEN')
DJANGO_EOL_API_TERC_URL = env('DJANGO_EOL_API_TERC_URL')

log = logging.getLogger(__name__)


def aluno_existe(codigo_eol):
    try:
        Aluno.objects.get(codigo_eol=codigo_eol)
        EOLService.atualiza_escola_dre(codigo_eol)
        return True
    except Aluno.DoesNotExist:
        return False


class EOLException(Exception):
    pass


class EOLService(object):
    DEFAULT_HEADERS = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}
    DEFAULT_HEADERS_TERC = {'Authorization': f'Token {DJANGO_EOL_API_TERC_TOKEN}'}
    DEFAULT_TIMEOUT = 20

    @classmethod
    def tem_informacao_faltando(cls, dados_responsavel):

        return (
            not dados_responsavel['nm_responsavel']
            or not dados_responsavel['dc_tipo_responsavel']
            or not dados_responsavel['cd_cpf_responsavel']
            or not dados_responsavel['nr_celular_responsavel']
            or not dados_responsavel['email_responsavel']
            or not dados_responsavel['nm_mae_responsavel']
            or not dados_responsavel['dt_nascimento_responsavel']
        )

    @classmethod
    def get_informacoes_responsavel(cls, codigo_eol):
        log.info(f"Buscando informações do responsável do eol: {codigo_eol}")
        if aluno_existe(codigo_eol):
            log.info("Informações do aluno já existente na base.")

            return AlunoService.get_aluno_serializer(codigo_eol)
        else:
            log.info('Buscando informações na API EOL.')
            response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                    headers=cls.DEFAULT_HEADERS,
                                    timeout=cls.DEFAULT_TIMEOUT)
            if response.status_code == status.HTTP_200_OK:
                results = response.json()['results']
                if len(results) == 1:
                    return results[0]
                raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
            else:
                raise EOLException(f'Código EOL não existe')

    @classmethod
    def get_cpf_eol_responsavel(cls, codigo_eol):
        log.info(f"Buscando CPF do responsável do eol: {codigo_eol}")
        response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 1:
                return ajusta_cpf(results[0].get('responsaveis')[0].get('cd_cpf_responsavel'))
            raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
        else:
            raise EOLException(f'Código EOL não existe')

    @classmethod
    def get_nome_eol_responsavel(cls, codigo_eol):
        log.info(f"Buscando nome do responsável pelo aluno de eol: {codigo_eol}")
        response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 1:
                return results[0]['responsaveis'][0].pop('nm_responsavel').strip()
            raise EOLException(f'Resultados para o código: {codigo_eol} vazios')
        else:
            raise EOLException(f'Código EOL não existe')

    @classmethod
    def registra_log(cls, codigo_eol, json):
        LogConsultaEOL.objects.create(codigo_eol=codigo_eol, json=json)

    @classmethod
    def get_informacoes_usuario(cls, registro_funcional):
        log.info(f"Buscando informações do usuário com RF: {registro_funcional}")
        response = requests.get(f'{DJANGO_EOL_API_TERC_URL}/cargos/{registro_funcional}',
                                headers=cls.DEFAULT_HEADERS_TERC,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            log.info(f"Dados usuário: {results}")
            if len(results) >= 1:
                return results
            raise EOLException(f'Resultados para o RF: {registro_funcional} vazios')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')

    @classmethod
    def get_alunos_escola(cls, cod_eol_escola):
        log.info(f"Buscando alunos de uma escola com o código EOL: {cod_eol_escola}")
        response = requests.get(f'{DJANGO_EOL_API_TERC_URL}/escola_turma_aluno/{cod_eol_escola}',
                                headers=cls.DEFAULT_HEADERS_TERC,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            log.info(f"Alunos da escola: {results}")
            if len(results) >= 1:
                if cod_eol_escola in ESCOLAS_CEI:
                    results = [aluno for aluno in results if
                               aluno.get('dc_serie_ensino') in ['INFANTIL I', 'INFANTIL II']]
                return [aluno for aluno in results if 'EJA' not in aluno.get('dc_serie_ensino')]
            raise EOLException(f'Resultados para o Código EOL: {cod_eol_escola} vazios')
        else:
            raise EOLException(f'API EOL com erro. Status: {response.status_code}')

    @classmethod
    def cpf_divergente(cls, codigo_eol, cpf):
        cpf_eol = ''
        response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if results and results[0]['responsaveis']:
                cpf_eol = ajusta_cpf(results[0]['responsaveis'][0].pop('cd_cpf_responsavel'))
            return cpf != cpf_eol

    @classmethod
    def nome_divergente(cls, codigo_eol, nome):
        nome_eol = ''
        response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if results and results[0]['responsaveis']:
                nome_eol = results[0]['responsaveis'][0].pop('nm_responsavel').strip()
            return remove_accents(nome).upper() != remove_accents(nome_eol).upper()

    @classmethod
    def cria_aluno_desatualizado(cls, codigo_eol):
        dados = cls.get_informacoes_responsavel(codigo_eol)
        cls.registra_log(codigo_eol, dados)
        if not dados['responsaveis']:
            raise EOLException('Código com cadastro incompleto. Falta cadastrar no EOL o(a) responsável ' +
                               'pela criança, para depois fazer a solicitação do uniforme')
        cpf = ajusta_cpf(dados['responsaveis'][0]['cd_cpf_responsavel'])
        data_nascimento = datetime.datetime.strptime(dados['dt_nascimento_aluno'], "%Y-%m-%dT%H:%M:%S")
        
        dados_responsavel = dados['responsaveis'][0]
        status = "ATUALIZADO_EOL" if not EOLService.tem_informacao_faltando(dados_responsavel) else 'DESATUALIZADO'
    
        responsavel = Responsavel.objects.create(
            vinculo=dados['responsaveis'][0]['tp_pessoa_responsavel'],
            codigo_eol_aluno=codigo_eol,
            nome=dados['responsaveis'][0]['nm_responsavel'].strip() if dados['responsaveis'][0][
                'nm_responsavel'] else None,
            cpf=cpf,
            ddd_celular=dados['responsaveis'][0]['cd_ddd_celular_responsavel'].strip() if dados['responsaveis'][0][
                'cd_ddd_celular_responsavel'] else None,
            celular=dados['responsaveis'][0]['nr_celular_responsavel'],
            status=status
        )
        aluno = Aluno.objects.create(
            codigo_eol=codigo_eol,
            data_nascimento=data_nascimento,
            nome=dados['nm_aluno'],
            codigo_escola=dados['cd_escola'],
            codigo_dre=dados['cd_dre'],
            responsavel=responsavel,
        )
        return aluno

    @classmethod
    def atualizar_dados_responsavel(cls, codigo_eol: str, vinculo: str, nome: str, cpf: str, ddd_celular: str,
                                    celular: str, tipo_turno_celular: str, email: str, nome_mae: str,
                                    data_nascimento: str):
        payload = {
            "usuario": "webResp",
            "senha": "resp",
            "cd_aluno": codigo_eol,
            "tp_pessoa_responsavel": vinculo,
            "nm_responsavel": nome,
            "cd_cpf_responsavel": cpf,
            "in_cpf_responsavel_confere": "S",
            "cd_ddd_celular_responsavel": ddd_celular if ddd_celular else "",
            "nr_celular_responsavel": celular if celular else "",
            "cd_tipo_turno_celular": tipo_turno_celular,
            "in_autoriza_envio_sms_responsavel": "S",
            "email_responsavel": email if email else "",
            "nm_mae_responsavel": nome_mae,
            "dt_nascimento_responsavel": data_nascimento,
            "nr_rg_responsavel": "",
            "cd_digito_rg_responsavel": "",
            "sg_uf_rg_responsavel": "",
            "cd_ddd_telefone_fixo_responsavel": "",
            "nr_telefone_fixo_responsavel": "",
            "cd_tipo_turno_fixo": "",
            "cd_ddd_telefone_comercial_responsavel": "",
            "nr_telefone_comercial_responsavel": "",
            "cd_tipo_turno_comercial": "",
        }

        log.info(f"Atualizando informações do responsavel pelo aluno: {codigo_eol} no eol")
        response = requests.post(DJANGO_EOL_API_ATUALIZAR_URL,
                                 auth=HTTPBasicAuth(USUARIO_EOL_API, SENHA_EOL_API),
                                 timeout=cls.DEFAULT_TIMEOUT,
                                 json=payload)

        if response.json() == 'TRUE - ATUALIZACAO EFETUADA COM SUCESSO':
            try:
                responsavel = Responsavel.objects.get(codigo_eol_aluno=codigo_eol, responsavel_alterado=False)
                responsavel.status = responsavel.STATUS_ATUALIZADO_EOL
                responsavel.save()
                log.info(f"Alterando status do responsavel pelo aluno: {codigo_eol} para STATUS_ATUALIZADO_EOL")
            except Responsavel.DoesNotExist:
                pass
        else:
            log.info(f"Erro ao atualizar dados do responsavel pelo aluno: {codigo_eol}. Erro: {response.json()}")
            LogErroAtualizacaoEOL.objects.create(codigo_eol=codigo_eol, cpf=cpf, nome=nome, erro=response.json())
            raise EOLException(f"Erro ao atualizar responsavel: {response.json()}")

    @classmethod
    def atualiza_escola_dre(cls, codigo_eol):
        aluno = Aluno.objects.filter(codigo_eol=codigo_eol)
        response = requests.get(f'{DJANGO_EOL_API_URL}/responsaveis/{codigo_eol}',
                                headers=cls.DEFAULT_HEADERS,
                                timeout=cls.DEFAULT_TIMEOUT)
        if response.status_code == status.HTTP_200_OK:
            results = response.json()['results']
            if len(results) == 1:
                aluno.update(
                    codigo_escola=results[0]['cd_escola'],
                    codigo_dre=results[0]['cd_dre']
                )
