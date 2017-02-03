# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 20:45
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JoinTargetInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('target_info', jsonfield.fields.JSONField()),
                ('is_valid_target_info', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name': 'Join Target information',
                'verbose_name_plural': 'Join Target information',
            },
        ),
    ]