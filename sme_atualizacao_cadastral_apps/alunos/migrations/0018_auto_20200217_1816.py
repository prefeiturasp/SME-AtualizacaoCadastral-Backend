# Generated by Django 2.2.9 on 2020-02-17 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0017_auto_20200217_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsavel',
            name='vinculo',
            field=models.IntegerField(choices=[(1, 'Mãe'), (2, 'Pai'), (3, 'Responsável Legal'), (4, 'Aluno Maior de Idade')], default=3, verbose_name='Vínculo'),
        ),
    ]
