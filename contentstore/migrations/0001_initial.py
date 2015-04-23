# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minute', models.CharField(default=b'*', max_length=64, verbose_name='minute')),
                ('hour', models.CharField(default=b'*', max_length=64, verbose_name='hour')),
                ('day_of_week', models.CharField(default=b'*', max_length=64, verbose_name='day of week')),
                ('day_of_month', models.CharField(default=b'*', max_length=64, verbose_name='day of month')),
                ('month_of_year', models.CharField(default=b'*', max_length=64, verbose_name='month of year')),
            ],
            options={
                'ordering': ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute'],
                'verbose_name': 'schedule',
                'verbose_name_plural': 'schedules',
            },
        ),
    ]
