# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 11:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20170217_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharewith',
            name='doc_id',
            field=models.IntegerField(null=True),
        ),
    ]
