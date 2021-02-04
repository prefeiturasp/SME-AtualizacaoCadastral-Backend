# Generated by Django 2.2.9 on 2020-03-11 19:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('enviado', models.BooleanField(default=False, verbose_name='Enviado?')),
                ('enviar_para', models.CharField(blank=True, max_length=255, null=True, verbose_name='Enviar Para')),
                ('assunto', models.CharField(blank=True, max_length=255, null=True, verbose_name='Assunto')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Enviar Para')),
            ],
            options={
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
        ),
    ]
