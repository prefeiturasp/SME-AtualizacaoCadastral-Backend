import csv
import environ
from sme_atualizacao_cadastral_apps.core.models import ListaPalavrasBloqueadas

ROOT_DIR = environ.Path(__file__) - 1


def cria_palavra_bloqueada(palavra):
    palavra_bloqueada, created = ListaPalavrasBloqueadas.objects.update_or_create(palavra=palavra)
    return palavra_bloqueada


class PalavraBloqueada(object):

    @classmethod
    def importa_palavras_bloqueadas(cls):
        with open(f'{ROOT_DIR}/lista_palavras_bloqueadas.csv', 'r') as file:
            lista_palavras = csv.reader(file, delimiter="|")
            next(lista_palavras)
            for palavra in lista_palavras:
                palavra = palavra[1]
                cria_palavra_bloqueada(palavra)
