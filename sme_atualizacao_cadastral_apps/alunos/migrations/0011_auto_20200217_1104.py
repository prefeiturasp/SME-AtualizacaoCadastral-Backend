# Generated by Django 2.2.9 on 2020-02-17 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0010_auto_20200217_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='servidor',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='RF do Dervidor'),
        ),
    ]
