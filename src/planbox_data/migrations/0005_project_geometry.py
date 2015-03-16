# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0004_roundup'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='geometry',
            field=models.fields.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
