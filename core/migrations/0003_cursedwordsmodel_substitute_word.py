# Generated by Django 4.2.5 on 2023-09-21 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_cursedwords_cursedwordsmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='cursedwordsmodel',
            name='substitute_word',
            field=models.CharField(default='*', max_length=100, verbose_name='Palavra_Substituta'),
            preserve_default=False,
        ),
    ]