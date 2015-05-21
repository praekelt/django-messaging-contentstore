# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import contentstore.models


class Migration(migrations.Migration):

    dependencies = [
        ('contentstore', '0002_messageset'),
    ]

    operations = [
        migrations.CreateModel(
            name='BinaryContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.FileField(upload_to=contentstore.models.generate_new_filename)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence_number', models.IntegerField()),
                ('lang', models.CharField(max_length=6)),
                ('text_content', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('binary_content', models.ForeignKey(related_name='message', to='contentstore.BinaryContent', null=True)),
                ('messageset', models.ForeignKey(related_name='messages', to='contentstore.MessageSet')),
            ],
        ),
    ]
