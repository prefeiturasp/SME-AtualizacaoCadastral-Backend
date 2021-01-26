from django.core.management.base import BaseCommand
from utility.carga_de_dados.import_palavras_bloqueadas import PalavraBloqueada


class Command(BaseCommand):
    help = 'Importa palavras bloqueadas.'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Importando...'))

        PalavraBloqueada.importa_palavras_bloqueadas()

        self.stdout.write(self.style.SUCCESS('Importação concluída:'))
