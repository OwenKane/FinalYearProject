# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_keys_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='keys',
            name='iv',
            field=models.TextField(null=True),
        ),
    ]
