from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import MinLengthValidator
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

from ..alunos.models import Aluno
from ..alunos.tasks import enviar_email_simples
from ..core.models_abstracts import TemChaveExterna
from ..core.utils import url_configs
from ..core.constants import CODIGOS_DRES


class User(SimpleEmailConfirmationUserMixin, AbstractUser, TemChaveExterna):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    cpf = CharField(_('CPF'), max_length=11, blank=True, null=True, unique=True,  # noqa DJ01
                    validators=[MinLengthValidator(11)])
    codigo_escola = CharField("Código EOL da Escola", max_length=10, blank=True, null=True)
    nome_escola = CharField("Nome da Escola", max_length=100, blank=True, null=True)
    codigo_dre = CharField("Código EOL da DRE", max_length=10, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def enviar_email_confirmacao(self):
        self.add_email_if_not_exists(self.email)
        content = {'uuid': self.uuid, 'confirmation_key': self.confirmation_key}
        conteudo = (f'Para confirmar seu e-mail e ativar seu cadastro no ambiente administrativo do Portal do ' +
                    f'Uniforme, clique neste link: ' +
                    f'{url_configs("CONFIRMAR_EMAIL", content)}')
        enviar_email_simples.delay(
            assunto='Confirme seu e-mail - Ambiente administrativo do Portal do Uniforme',
            mensagem=conteudo,
            enviar_para=self.email
        )

    def enviar_email_recuperacao_senha(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self)
        content = {'uuid': self.uuid, 'confirmation_key': token}
        titulo = 'Recuperação de senha'
        conteudo = (f'Clique neste link para criar uma nova senha no ambiente administrativo do Portal do Uniforme: ' +
                    f'{url_configs("RECUPERAR_SENHA", content)}')
        enviar_email_simples.delay(
            assunto=titulo,
            mensagem=conteudo,
            enviar_para=self.email
        )

    def get_alunos_nao_desatualizados(self):
        lista_codigo_eol = list(
            Aluno.objects.filter(
                codigo_escola=self.codigo_escola
            ).exclude(responsavel__status='DESATUALIZADO').values('codigo_eol')
        )
        return [int(aluno['codigo_eol']) for aluno in lista_codigo_eol]

    def atualiza_senha(self, senha, token):
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(self, token):
            self.set_password(senha)
            self.save()
            return True
        return False

    @property
    def perfil_usuario(self):
        if not self.codigo_escola or not self.codigo_dre:
            return "perfil_indisponivel"
        elif self.codigo_dre not in CODIGOS_DRES:
            return 'perfil_sme'
        elif self.codigo_escola != self.codigo_dre:
            return 'perfil_escola'
        elif self.codigo_dre in CODIGOS_DRES:
            return 'perfil_dre'
        else:
            return 'perfil_indisponivel'
