# Generated by Django 2.2.9 on 2021-08-10 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0002_auto_20210810_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCadastro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpf', models.CharField(max_length=11, verbose_name='CPF')),
                ('situacao', models.IntegerField(choices=[(1, '1 - Dirija-se a DRE'), (2, '2 - Dirija-se a unidade escolar'), (3, '3 - Cadastro completo')], default=2, verbose_name='Situação')),
            ],
            options={
                'verbose_name': 'Base de cadastro',
                'verbose_name_plural': 'Base de cadastros',
            },
        ),
    ]
