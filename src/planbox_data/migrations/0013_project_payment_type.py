# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planbox_data', '0012_project_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='payment_type',
            field=models.CharField(default='', max_length=20, blank=True),
            preserve_default=False,
        ),
    ]
