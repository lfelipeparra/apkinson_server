# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-08-17 21:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apkinson_mobile', '0002_auto_20190817_2056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paciente',
            old_name='genero',
            new_name='gender',
        ),
        migrations.RenameField(
            model_name='paciente',
            old_name='nombres',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='edad',
        ),
    ]
