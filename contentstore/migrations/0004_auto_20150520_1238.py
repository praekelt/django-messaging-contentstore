# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contentstore', '0003_binarycontent_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['sequence_number']},
        ),
    ]
