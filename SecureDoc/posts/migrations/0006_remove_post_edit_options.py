# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 10:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_sharewith'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='edit_options',
        ),
    ]
