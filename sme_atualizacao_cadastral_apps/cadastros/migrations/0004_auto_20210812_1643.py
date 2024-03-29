# Generated by Django 2.2.9 on 2021-08-12 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0003_basecadastro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planilhasituacao',
            name='arquivo',
            field=models.FileField(help_text='Arquivo no formato <strong>.xlsx</strong> com duas colunas, sendo os seguintes titulos:<strong>CD_CPF_RESPONSAVEL e MSG</strong> | A primeira coluna deve conter apenas os números do CPF e a segunda coluna apenas o número da situação', upload_to='situacao_cadastro/planilhas', verbose_name='Planilha'),
        ),
    ]
