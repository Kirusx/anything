# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-12-29 10:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectLog',
            fields=[
                ('project_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('project_name', models.CharField(max_length=100)),
                ('project_grey_ip', models.GenericIPAddressField()),
                ('project_online_ip', models.GenericIPAddressField()),
                ('project_dept_name', models.CharField(max_length=100)),
            ],
        ),
    ]