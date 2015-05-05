# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contentstore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(unique=True, max_length=20, verbose_name='Short name')),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('default_schedule', models.ForeignKey(related_name='message_sets', to='contentstore.Schedule')),
                ('next_set', models.ForeignKey(blank=True, to='contentstore.MessageSet', null=True)),
            ],
        ),
    ]
