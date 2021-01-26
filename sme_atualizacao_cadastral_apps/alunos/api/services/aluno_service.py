from ...models import Aluno


class AlunoService(object):

    @classmethod
    def get_aluno_serializer(cls, codigo_eol):
        from ..serializers.aluno_serializer import AlunoSerializer

        aluno = Aluno.objects.get(codigo_eol=codigo_eol)
        aluno_serializer = AlunoSerializer(aluno).data
        responsaveis = [aluno_serializer['responsaveis']]
        aluno_serializer['responsaveis'] = responsaveis
        return aluno_serializer
