# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_remove_post_nominated'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareWith',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField()),
                ('author', models.CharField(max_length=200)),
                ('nominated_user', models.CharField(max_length=200)),
                ('edit_options', models.BooleanField(default=False)),
            ],
        ),
    ]