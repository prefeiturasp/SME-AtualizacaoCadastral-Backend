# Generated by Django 2.2.9 on 2021-08-12 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0004_auto_20210812_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogProcessamentoPlanilha',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.CharField(max_length=255, null=True, verbose_name='Nome do arquivo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('status', models.BooleanField(default=False, editable=False, verbose_name='Status')),
                ('msg_retorno', models.TextField(verbose_name='Mensagem')),
            ],
            options={
                'verbose_name': 'Log de processamento',
                'verbose_name_plural': 'Logs de processamento',
            },
        ),
    ]