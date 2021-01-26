# Generated by Django 2.2.9 on 2020-02-07 20:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0006_auto_20200207_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logconsultaeol',
            name='codigo_eol',
            field=models.CharField(max_length=7, validators=[django.core.validators.MinLengthValidator(7)], verbose_name='Código EOL do Aluno'),
        ),
    ]
