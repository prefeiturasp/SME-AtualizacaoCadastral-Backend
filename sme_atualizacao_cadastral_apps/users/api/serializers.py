from rest_framework import serializers

from sme_atualizacao_cadastral_apps.eol_servico.utils import EOLService
from sme_atualizacao_cadastral_apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    perfil_usuario = serializers.CharField(required=False)

    def get_informacoes_usuario(self, validated_data):
        return EOLService.get_informacoes_usuario(validated_data['username'])

    def create(self, validated_data):  # noqa C901
        informacoes_usuario_json = self.get_informacoes_usuario(validated_data)
        cpf = informacoes_usuario_json[0]['cd_cpf_pessoa']
        assert cpf == validated_data['cpf'], 'CPF divergente'
        email = f'{validated_data["email"]}@sme.prefeitura.sp.gov.br'
        usuario = User.objects.create_user(
            email=email,
            password=validated_data['password'],
            username=validated_data['username']
        )
        usuario.name = informacoes_usuario_json[0]['nm_pessoa']
        usuario.codigo_escola = informacoes_usuario_json[0]['cd_divisao']
        usuario.nome_escola = informacoes_usuario_json[0]['divisao']
        usuario.codigo_dre = informacoes_usuario_json[0]['cd_coord']
        usuario.cpf = cpf
        usuario.is_active = False
        usuario.save()
        return usuario

    class Meta:
        model = User
        fields = ("username", "email", "name", "cpf", "nome_escola", "perfil_usuario")
